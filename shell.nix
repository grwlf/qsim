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



  bespon = pkgs.python37Packages.buildPythonPackage rec {
    pname = "bespon_py";
    version = "0.6.0";
    # propagatedBuildInputs = with mypython.pkgs ; [nr-types pyyaml];
    # doCheck = false; # local HTTP requests don't work
    src = pkgs.fetchFromGitHub {
      owner = "gpoore";
      repo = pname;
      rev = "183d0a49146025969266fc1b4157392d5ffda609";
      sha256 = "sha256:0x1ifklhh88fa6i693zgpb63646jxsyhj4j64lrvarckrb31wk23";
    };
  };


  codebraid = pkgs.python37Packages.buildPythonPackage rec {
    pname = "codebraid";
    version = "0.4.0";

    propagatedBuildInputs =  with pkgs.python37.pkgs ; [bespon];
    # propagatedBuildInputs = with mypython.pkgs ; [six deprecated];
    # patchPhase = ''
    #   sed -i 's/typing//' setup.py
    # '';
    src = pkgs.fetchFromGitHub {
      owner = "gpoore";
      repo = pname;
      rev = "c7931c4b98ff929b763e645633ab51939d664c7a";
      sha256 = "sha256:0wxpz3gb6mw29c2dn8a8c37gmyhckallsd2kqnjnjqvhadxnb942";
    };
  };

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
      codebraid
      pandoc
    ]);

    shellHook = with pkgs; ''
      if test -f ./env.sh ; then
        . ./env.sh
      fi
    '';
  };

in
  be
