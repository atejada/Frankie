class Frankie < Formula
  desc "Terminal-native language stitched from Ruby, Python, R, and Fortran"
  homepage "https://github.com/atejada/Frankie"
  # v1.22.3+: points at an uploaded release ASSET, not GitHub's
  # auto-generated tag archive — the auto-generated one doesn't get a
  # tracked download_count, so there was no way to see install activity
  # for this tap. .github/workflows/release.yml builds + uploads this
  # asset on every `vX.Y.Z` tag push and prints the values below in the
  # Actions run summary; see packaging/homebrew/README.md.
  url "https://github.com/atejada/Frankie/releases/download/v1.22.3/frankie-1.22.3.tar.gz"
  sha256 "REPLACE_WITH_TARBALL_SHA256"   # from the workflow run's summary for v1.22.3
  license "GPL-3.0-only"

  depends_on "python@3.12"

  def install
    # Frankie is pure Python stdlib — install the whole tree and shim the CLI
    libexec.install Dir["*"]
    (bin/"frankiec").write <<~SHELL
      #!/bin/bash
      exec "#{Formula["python@3.12"].opt_bin}/python3.12" "#{libexec}/frankiec.py" "$@"
    SHELL
    chmod 0755, bin/"frankiec"
  end

  def caveats
    <<~EOS
      Get started:
        frankiec repl
        frankiec new --game mygame && cd mygame && frankiec run main.fk

      Standard stitches ship with the install; project-local ./stitches and
      ~/.frankie/stitches take precedence. Editor support: frankiec lsp

      Bundled examples (Snake, Pong, Zombie Invaders, and more):
        frankiec examples            # list them
        frankiec examples snake      # copy one here, then: cd snake && frankiec run main.fk
      They live in: #{opt_libexec}/examples
    EOS
  end

  test do
    assert_match "Frankie v", shell_output("#{bin}/frankiec version")

    (testpath/"hello.fk").write <<~FRANKIE
      def greet(name: String) -> String
        "hello, \#{name}!"
      end
      puts greet("brew")
    FRANKIE
    assert_match "hello, brew!", shell_output("#{bin}/frankiec run #{testpath}/hello.fk")

    # stitches resolve from the installed tree
    (testpath/"color.fk").write('stitch "frankiecolor"' + "\n" + 'puts green("ok")')
    assert_match "ok", shell_output("#{bin}/frankiec run #{testpath}/color.fk")
  end
end
