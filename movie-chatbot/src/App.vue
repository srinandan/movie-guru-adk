<!--
 Copyright 2025 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->


<script setup>
import { ref, onMounted, reactive, nextTick } from 'vue';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

const sessionId = ref(null);
const messages = ref([]);
const userInput = ref('');
const featuredMovies = ref([]);

onMounted(async () => {
  try {
    // Fetch featured movies
    const featuredMoviesResponse = await fetch(`${apiBaseUrl}/random`);
    if (featuredMoviesResponse.ok) {
      const featuredMoviesData = await featuredMoviesResponse.json();
      featuredMovies.value = featuredMoviesData.map(movie => ({ name: movie.title, poster: movie.poster }));
    } else {
      console.error('Failed to fetch featured movies:', featuredMoviesResponse.statusText);
    }

    // Create session
    const sessionResponse = await fetch(`${apiBaseUrl}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-authenticated-user-email': 'srinandans@google.com',
      },
      body: JSON.stringify({
        state: {
          login: true
        }
      }),
    });
    const data = await sessionResponse.json();
    sessionId.value = data.session_id;
    messages.value.push({ author: 'system', text: 'Session created. How can I help you today?' });
  } catch (error) {
    console.error('Error creating session:', error);
    messages.value.push({ author: 'system', text: 'Error creating session. Please refresh the page.' });
  }
});

const sendMessage = async () => {
  if (!userInput.value.trim() || !sessionId.value) return;

  const userMessage = userInput.value;
  messages.value.push({ author: 'user', text: userMessage });
  userInput.value = '';

  const agentMessage = reactive({ author: 'agent', text: 'Typing...' });
  messages.value.push(agentMessage);

  const payload = {
    appName: 'app',
    userId: 'srinandans@google.com',
    sessionId: sessionId.value,
    newMessage: {
      role: 'user',
      parts: [
        {
          text: userMessage,
        },
      ],
    },
    streaming: false,
  };

  try {
    const response = await fetch(`${apiBaseUrl}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-authenticated-user-email': 'srinandans@google.com',
      },
      body: JSON.stringify(payload),
    });

    if (response.status === 422) {
        const errorText = await response.text();
        console.error('Error sending message: 422 Unprocessable Entity', errorText);
        agentMessage.text = `Error sending message: ${errorText}`;
        return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    agentMessage.text = '';

    if (Array.isArray(data)) {
        let movieDataFound = false;
        for (const item of data) {
            if (item.content && item.content.parts && item.content.parts.length > 0 && item.content.parts[0].text && item.content.parts[0].text.includes('"movies"')) {
                const text = item.content.parts[0].text;
                const jsonString = text.replace(/```json\n|```/g, '');
                try {
                    const movieData = JSON.parse(jsonString);
                    if (movieData.movies) {
                        agentMessage.text = 'Here are some movies you might like:';
                        movieData.movies.forEach(movie => {
                            messages.value.push({
                                author: 'movie',
                                ...movie
                            });
                        });
                        movieDataFound = true;
                        break; // Exit loop once movie data is found
                    }
                } catch (e) {
                    console.error('Error parsing movie JSON:', e);
                    agentMessage.text = "Sorry, I couldn't parse the movie recommendations.";
                }
            }
        }
        if (!movieDataFound) {
            // If no movies were found, check for a standard text response in the first element
            if (data[0] && data[0].content && data[0].content.parts && data[0].content.parts.length > 0 && data[0].content.parts[0].text) {
                agentMessage.text = data[0].content.parts[0].text;
            } else {
                agentMessage.text = "Sorry, I didn't get a response. Please try again.";
            }
        }
    } else if (data.content && data.content.parts && data.content.parts.length > 0) {
      // This is a text response
      const part = data.content.parts[0];
      if (part.text) {
        agentMessage.text = part.text;
      }
    } else {
      agentMessage.text = "Sorry, I didn't get a response. Please try again.";
    }
    await nextTick(); // Force UI update

  } catch (error) {
    console.error('Error sending message:', error);
    agentMessage.text = 'Error sending message. Please try again.';
  }
};
</script>

<template>
  <div id="main-container">
    <div id="featured-movies-container" v-if="featuredMovies.length > 0">
      <h2>Featured Movies</h2>
      <div class="featured-movie-card" v-for="movie in featuredMovies" :key="movie.name">
        <img :src="movie.poster" :alt="movie.name" />
        <p>{{ movie.name }}</p>
      </div>
    </div>
    <div id="app-container">
      <div id="title-container">
        <h1>Movie Guru</h1>
        <p>Your personal movie recommendation assistant. Ask for movie suggestions, get plot summaries, and see movie posters.</p>
      </div>
      <div id="chat-container">
        <div id="chat-window">
          <div v-for="(message, index) in messages" :key="index" :class="['message', message.author]">
            <img v-if="message.author === 'agent'" src="/bot-avatar.png" class="avatar" alt="Bot Avatar" />
            <div v-if="message.author !== 'movie'">
              <p>{{ message.text }}</p>
              <img v-if="message.image_url" :src="message.image_url" alt="Movie Poster" />
            </div>
            <div v-if="message.author === 'movie'" class="movie-card">
              <img :src="message.poster" :alt="message.name" />
              <div class="movie-details">
                <h3>{{ message.name }} ({{ message.released }})</h3>
                <p><strong>Rating:</strong> {{ message.rating }}</p>
                <p>{{ message.plot }}</p>
              </div>
            </div>
          </div>
        </div>
        <div id="input-container">
          <input v-model="userInput" @keyup.enter="sendMessage" placeholder="Type your message..." />
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
#main-container {
  display: flex;
}

#featured-movies-container {
  width: 25%;
  padding: 2rem;
  border-right: 1px solid #ccc;
}

.featured-movie-card {
  margin-bottom: 1.5rem;
  text-align: center;
}

.featured-movie-card img {
  width: 100%;
  border-radius: 8px;
}

#app-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center chat window */
  width: 75%;
  padding: 2rem;
}

#title-container {
  width: 100%; /* Full width of the app container */
  text-align: center;
  margin-bottom: 2rem;
}

#chat-container {
  display: flex;
  flex-direction: column;
  height: 75vh; /* Reduced height */
  width: 100%; /* Full width of the app container */
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
}

#chat-window {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  max-width: 80%;
}

.user {
  background-color: #dcf8c6;
  align-self: flex-end;
}

.agent {
  background-color: #f1f0f0;
  align-self: flex-start;
  display: flex;
  align-items: center;
}

.system {
  background-color: #f0f0f0;
  align-self: center;
  text-align: center;
  font-style: italic;
}

#input-container {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #ccc;
}

input {
  flex-grow: 1;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  margin-left: 1rem;
  padding: 0.5rem 1rem;
  border: none;
  background-color: #4caf50;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

img {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 0.5rem;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 1rem;
}

.movie-card {
  display: flex;
  gap: 1rem;
}

.movie-card img {
  width: 200px;
  height: auto;
}

.movie-details {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}
</style>
