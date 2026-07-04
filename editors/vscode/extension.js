// Frankie Language extension — launches `frankiec lsp` (v1.18).
//
// Building the extension locally:
//   cd editors/vscode && npm install && npx vsce package
//
// The language server itself is pure Python stdlib (frankie_lsp.py) — the
// only npm dependency is the standard VS Code LSP client glue below.

const vscode = require('vscode');

let client = null;

function activate(context) {
  let LanguageClient, TransportKind;
  try {
    ({ LanguageClient, TransportKind } = require('vscode-languageclient/node'));
  } catch (e) {
    // vscode-languageclient not installed (grammar-only build) —
    // syntax highlighting still works, LSP features are disabled.
    console.warn('frankie-language: vscode-languageclient not found; ' +
                 'run `npm install` in editors/vscode to enable the LSP.');
    return;
  }

  const command = vscode.workspace.getConfiguration('frankie')
                        .get('lspCommand', 'frankiec');

  const serverOptions = {
    command: command,
    args: ['lsp'],
    transport: TransportKind.stdio,
  };

  const clientOptions = {
    documentSelector: [{ scheme: 'file', language: 'frankie' }],
  };

  client = new LanguageClient(
    'frankie-lsp', 'Frankie Language Server', serverOptions, clientOptions);
  client.start();
  context.subscriptions.push({ dispose: () => client && client.stop() });
}

function deactivate() {
  return client ? client.stop() : undefined;
}

module.exports = { activate, deactivate };
