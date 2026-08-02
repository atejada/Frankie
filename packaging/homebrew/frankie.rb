class Frankie < Formula
  desc "Terminal-native language stitched from Ruby, Python, R, and Fortran"
  homepage "https://github.com/atejada/Frankie"
  url "https://github.com/atejada/Frankie/archive/refs/tags/v1.20.0.tar.gz"
  sha256 "REPLACE_WITH_TARBALL_SHA256"   # see packaging/homebrew/README.md
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
