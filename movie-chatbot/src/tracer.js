import * as opentelemetry from '@opentelemetry/sdk-node';
import {
  getNodeAutoInstrumentations,
  getResourceDetectors as getResourceDetectorsFromEnv,
} from '@opentelemetry/auto-instrumentations-node';


// [START opentelemetry_instrumentation_setup_opentelemetry]


const sdk = new opentelemetry.NodeSDK({
  instrumentations: getNodeAutoInstrumentations({
    // Disable noisy instrumentations
    '@opentelemetry/instrumentation-fs': {enabled: false},
  }),
  resourceDetectors: getResourceDetectorsFromEnv(),
});

try {
  sdk.start();
  diag.info('OpenTelemetry automatic instrumentation started successfully');
} catch (error) {
  diag.error(
    'Error initializing OpenTelemetry SDK. Your application is not instrumented and will not produce telemetry',
    error
  );
}

// Gracefully shut down the SDK to flush telemetry when the program exits
process.on('SIGTERM', () => {
  sdk
    .shutdown()
    .then(() => diag.debug('OpenTelemetry SDK terminated'))
    .catch(error => diag.error('Error terminating OpenTelemetry SDK', error));
});
// [END opentelemetry_instrumentation_setup_opentelemetry]

export default sdk;