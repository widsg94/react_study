// craco.config.js
module.exports = {
  webpack: {
      configure: (webpackConfig) => {
          webpackConfig.resolve.fallback = {
              ...webpackConfig.resolve.fallback, // Keep existing fallbacks
              zlib: require.resolve("browserify-zlib"),
              path: require.resolve("path-browserify"),
          };
          return webpackConfig;
      },
  },
};
