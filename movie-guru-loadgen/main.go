// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"log/slog"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"time"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"golang.org/x/time/rate"
)

const userPrompt = `You are a %d year oldperson who is chatting with a knowledgeable film expert. 
You are not a film expert and need information from the movie expert. The only information you have is what the expert tells you.
You cannot use any external knowledge about real movies or information to ask questions, even if you have access to it. You only can derive context from the expert's response.
The genres you are interested in may be one or a combination of the following: comedy, horror, kids, cartoon, thriller, adeventure, fantasy.
You are only interested in movies from the year 2000 onwards.
You can ask questions about the movie, any actors, directors. Or you can ask the expert to show you movies of a specific type (genre, short duration, from a specific year, movies that are similar to a specific movie, etc.)
You must ask the question in 750 characters or less.

**Your Task:**

Engage in a natural conversation with the expert, reacting to their insights and asking questions just like a real movie buff would.`

const (
	ageMin      = 18
	ageMax      = 80
	fakeUser    = "fake@google.com"
	appName     = "app"
	address     = "0.0.0.0:"
	defaultPort = "8080"
)

var (
	maxChatLen = 750
	limiter    *rate.Limiter
)

// OllamaRequest represents the payload sent to the Ollama API
type OllamaRequest struct {
	Model  string `json:"model"`
	Prompt string `json:"prompt"`
	Stream bool   `json:"stream"` // Set to false to get the full response at once
}

// OllamaResponse represents the response from the Ollama API when streaming is false
type OllamaResponse struct {
	Model     string    `json:"model"`
	CreatedAt time.Time `json:"created_at"`
	Response  string    `json:"response"`
	Done      bool      `json:"done"`
}

type newMessage struct {
	Role  string `json:"role"`
	Parts []part `json:"parts"`
}

type part struct {
	Text string `json:"text"`
}

type AdkRequest struct {
	AppName    string     `json:"appName"`
	UserId     string     `json:"userId"`
	SessionId  string     `json:"sessionId"`
	NewMessage newMessage `json:"newMessage"`
	Streaming  bool       `json:"streaming"`
}

var chatServer, promptServer string

func getLogLevel() slog.Level {
	levelStr := os.Getenv("LOG_LEVEL")
	switch levelStr {
	case "DEBUG":
		return slog.LevelDebug
	case "INFO":
		return slog.LevelInfo
	case "WARN":
		return slog.LevelWarn
	case "ERROR":
		return slog.LevelError
	default:
		return slog.LevelInfo // Default to INFO
	}
}

func replacer(groups []string, a slog.Attr) slog.Attr {
	// Rename attribute keys to match Cloud Logging structured log format
	switch a.Key {
	case slog.LevelKey:
		a.Key = "severity"
		// Map slog.Level string values to Cloud Logging LogSeverity
		// https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity
		if level := a.Value.Any().(slog.Level); level == slog.LevelWarn {
			a.Value = slog.StringValue("WARNING")
		}
	case slog.TimeKey:
		a.Key = "timestamp"
	case slog.MessageKey:
		a.Key = "message"
	}
	return a
}

func setupLogging() {
	// Use json as our base logging format.
	jsonHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{ReplaceAttr: replacer, Level: getLogLevel(), AddSource: true})
	// Set this handler as the global slog handler.
	slog.SetDefault(slog.New(jsonHandler))
}

func main() {
	var wait time.Duration

	r := mux.NewRouter()
	r.HandleFunc("/", HealthHandler).Methods("GET")

	// Create a new CORS handler with specific options.
	corsHandler := cors.New(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowCredentials: true,
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type, Authorization", "ApiKey", "User"},
		Debug:            false,
	})

	srv := &http.Server{
		Addr:         address + defaultPort,
		WriteTimeout: time.Second * 15,
		ReadTimeout:  time.Second * 15,
		IdleTimeout:  time.Second * 60,
		Handler:      corsHandler.Handler(r),
	}

	setupLogging()

	var sessionId string
	var err error

	if os.Getenv("PROMPT_SERVER") != "" {
		promptServer = os.Getenv("PROMPT_SERVER")
	} else {
		slog.Log(context.Background(), slog.LevelError, "PROMPT_SERVER not set")
		return
	}

	if os.Getenv("CHAT_SERVER") != "" {
		chatServer = os.Getenv("CHAT_SERVER")
	} else {
		slog.Log(context.Background(), slog.LevelError, "CHAT_SERVER not set")
		return
	}

	sessionId, err = createSession()
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error creating session", "error", err)
		return
	}

	if os.Getenv("RATE_LIMIT") != "" {
		if r, err := strconv.ParseFloat(os.Getenv("RATE_LIMIT"), 64); err != nil {
			slog.Log(context.Background(), slog.LevelWarn, "Error parsing RATE_LIMIT, using defaults", "error", err)
			r = 5.0
		} else {
			limiter = rate.NewLimiter(rate.Limit(r/60.0), 1)
		}
	} else {
		// Rate limiter: 5 requests per minute
		limiter = rate.NewLimiter(rate.Limit(5.0/60.0), 1)
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil {
			log.Println(err)
		}
	}()

	go func() {
		for { // Infinite loop
			randomNumber := rand.Intn(ageMax-ageMin+1) + ageMin
			fullPrompt := fmt.Sprintf(userPrompt, randomNumber)
			moviePrompt, err := generatePrompt(fullPrompt)
			if err != nil {
				slog.Log(context.Background(), slog.LevelError, "Error generating prompt", "error", err)
				os.Exit(1)
			}

			err = requestMovieRecommendations(moviePrompt, sessionId)
			if err != nil {
				slog.Log(context.Background(), slog.LevelError, "Error requesting movie recommendations", "error", err)
				os.Exit(1)
			}

			time.Sleep(1 * time.Second) // Add a delay between requests if needed.
		}
	}()

	c := make(chan os.Signal, 1)
	// We'll accept graceful shutdowns when quit via SIGINT (Ctrl+C)
	// SIGKILL, SIGQUIT or SIGTERM (Ctrl+/) will not be caught.
	signal.Notify(c, os.Interrupt)

	// Block until we receive our signal.
	<-c

	// Create a deadline to wait for.
	ctx, cancel := context.WithTimeout(context.Background(), wait)
	defer cancel()
	// Doesn't block if no connections, but will otherwise wait
	// until the timeout deadline.
	_ = srv.Shutdown(ctx)

	slog.Log(context.Background(), slog.LevelInfo, "Shutting down")

	os.Exit(0)

}

func createSession() (string, error) {

	var sessionInfo map[string]string

	req, err := http.NewRequest("POST", chatServer+"/sessions", bytes.NewBuffer([]byte("{\"state\":{\"login\":true}}")))
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error creating request", "error", err)
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-goog-authenticated-user-email", fakeUser)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error sending request", "error", err)
		return "", err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		bodyBytes, _ := io.ReadAll(resp.Body)
		slog.Log(context.Background(), slog.LevelError, "Server returned error", "error", string(bodyBytes))
		return "", fmt.Errorf("server returned error: %s (%d)", http.StatusText(resp.StatusCode), resp.StatusCode)
	}

	b, _ := io.ReadAll(resp.Body)

	err = json.Unmarshal(b, &sessionInfo)
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error unmarshaling JSON", "error", err)
		return "", err
	}
	slog.Log(context.Background(), slog.LevelInfo, "Session created", "info", sessionInfo["session_id"])

	defer resp.Body.Close()

	return sessionInfo["session_id"], nil
}

func generatePrompt(fullPrompt string) (string, error) {

	slog.Debug("Sending prompt to Gemma", userPrompt)

	// Create the request payload
	requestPayload := OllamaRequest{
		Model:  "gemma3:4b",
		Prompt: fullPrompt,
		Stream: false,
	}

	// Convert the payload to JSON
	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error marshalling JSON", "error", err)
		return "", err
	}

	// Create a new HTTP POST request
	req, err := http.NewRequest("POST", promptServer+"/api/generate", bytes.NewBuffer(jsonData))
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error creating request", "error", err)
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")

	// Send the request using the default HTTP client
	client := &http.Client{Timeout: 60 * time.Second} // Set a timeout
	resp, err := client.Do(req)
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error sending request to Ollama", "error", err)
		return "", err
	}
	defer resp.Body.Close()

	// Check the response status code
	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		slog.Log(context.Background(), slog.LevelError, "Received non-OK HTTP status", resp.StatusCode, "Response", string(bodyBytes))
		return "", fmt.Errorf("received non-OK HTTP status %d", resp.StatusCode)
	}

	// Read the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		slog.Error("Error reading response body: %v", err)
		return "", err
	}

	// Unmarshal the JSON response
	var ollamaResponse OllamaResponse
	err = json.Unmarshal(body, &ollamaResponse)
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error unmarshalling response JSON", "error", err)
		return "", err
	}

	// Print the response from the model
	slog.Log(context.Background(), slog.LevelError, "Gemma's Response", "info", ollamaResponse.Response)
	return ollamaResponse.Response, nil
}

func requestMovieRecommendations(prompt string, sessionId string) error {
	// Create the request payload
	requestPayload := AdkRequest{
		AppName:   appName,
		UserId:    fakeUser,
		SessionId: "session_fake@google.com_476b8101", //sessionId,
		NewMessage: newMessage{
			Role: "user",
			Parts: []part{
				{
					Text: prompt,
				},
			},
		},
		Streaming: false,
	}
	// Convert the payload to JSON
	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error marshalling JSON", "error", err)
		return err
	}
	slog.Log(context.Background(), slog.LevelInfo, "Sending request to chat server", "info", string(jsonData))
	req, _ := http.NewRequest("POST", chatServer+"/run", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-goog-authenticated-user-email", fakeUser)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		slog.Log(context.Background(), slog.LevelError, "Error making request:", "Error", err)
		return err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		bodyBytes, _ := io.ReadAll(resp.Body)
		slog.Log(context.Background(), slog.LevelError, "Server returned error", "error", string(bodyBytes))
		return fmt.Errorf("server returned error: %s (%d)", http.StatusText(resp.StatusCode), resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	slog.Log(context.Background(), slog.LevelError, "Movie Recommendations", "info", string(body))
	defer resp.Body.Close()
	return nil
}

// HealthHandler handles kubernetes healthchecks
func HealthHandler(w http.ResponseWriter, r *http.Request) {
	_ = json.NewEncoder(w).Encode(map[string]bool{"ok": true})
}
