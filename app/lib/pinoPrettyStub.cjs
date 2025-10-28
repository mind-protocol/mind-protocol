/**
 * Minimal stub for pino-pretty so Next.js bundler doesn't fail when optional
 * pretty transport isn't installed in the workspace.
 *
 * pino expects this module to export a function that returns a stream-like
 * object. We provide a no-op transform that simply forwards input.
 */
module.exports = function pinoPrettyStub() {
  return {
    write(chunk) {
      return chunk;
    },
    pipe(dest) {
      return dest;
    }
  };
};
