#{ pkgs ?  import ./lib/nixpkgs {}
{ pkgs ?  import <nixpkgs> {}
, stdenv ? pkgs.stdenv
, with_cuda ? true
} :
let

  self = pkgs.python37Packages;
  inherit (pkgs) fetchurl fetchgit fetchFromGitHub;
  inherit (self) buildPythonPackage fetchPypi;

  pyls = self.python-language-server.override { providers=["pycodestyle"]; };
  pyls-mypy = self.pyls-mypy.override { python-language-server=pyls; };


  my-python-packages = pp: with pp; [
      pandas
      ipython
      pytest-mypy
      ipdb
      hypothesis
      scipy
    ];
  python-with-my-packages = pkgs.python37.withPackages my-python-packages;

  be = pkgs.mkShell {
    name = "pythonshell";
    buildInputs =
    [
      pyls-mypy
      pyls
    ] ++
    ( with pkgs;
      with self;
    [
      strace
      gdb
      ipython
      python-with-my-packages
    ]);

    shellHook = with pkgs; ''
      if test -f ./env.sh ; then
        . ./env.sh
      fi
    '';
  };

in
  be
