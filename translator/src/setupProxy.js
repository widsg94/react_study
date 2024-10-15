const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        '/api', // This is the local path you will call
        createProxyMiddleware({
            target: 'https://labs.goo.ne.jp/api', // The base URL of the API
            changeOrigin: true,
            pathRewrite: {
                '^/api': '', // This rewrites the URL by removing the '/api' prefix
            },
        })
    );
};