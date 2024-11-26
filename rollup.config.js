export default {
    input: 'Wallet.js', // Entry file
    output: {
      file: 'dist/bundle.js', // Output bundled file
      format: 'iife', // Immediately Invoked Function Expression for browsers
      name: 'WalletModule', // Makes `Wallet` accessible as `WalletModule.Wallet`
    },
  };