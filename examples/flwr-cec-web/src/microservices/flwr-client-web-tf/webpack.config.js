const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = () => {
	return {
		// target: ['web'],
        context: __dirname,
		entry: './src/index.ts',
		output: {
			path: path.resolve(__dirname, 'dist'),
			filename: 'bundle.js',
			library: 'client',
            libraryTarget: 'umd',
		},
         module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                    },
                }, 
                {
                    test: /\.tsx?$/,
                    use: 'ts-loader',
                    exclude: /node_modules/,
                },
                {
                    test: /\.css$/i,
                    use: ['style-loader', 'css-loader'],
                }]},
		plugins: [
            new HtmlWebpackPlugin({
                template: './public/index.html'
        }),
        new CopyWebpackPlugin({
            patterns: [
              {
                from: path.resolve(__dirname, 'node_modules/@tensorflow/tfjs-backend-wasm/dist/'),
                to: 'dist/',
              },
            ],
          })],
        devServer: {
            hot: true,
            static: {
                directory: path.join(__dirname, 'public'),
            },
            compress: true,
            port: 9000
        },
		mode: 'production',
		resolve: {
			extensions: ['.ts', '.js', '.tsx'],
            fallback: {
                crypto: require.resolve('crypto-browserify'),
                stream: require.resolve("stream-browserify"),
                buffer: require.resolve("buffer/"),
            }
		}
	}
};