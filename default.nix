{ pkgs ?  import <nixpkgs> {}
, python ? pkgs.python37
, doCheck ? true
} :

with python.pkgs;
buildPythonPackage {
  pname = "qsim";
  version = "1.0.0";
  src = builtins.filterSource (
    path: type: !( baseNameOf path == "build" && type == "directory" ) &&
                !( baseNameOf path == "result" )
    ) ./.;

  preConfigure = ''
    export PATH="${pkgs.git}/bin:$PATH"
    if ! test -d /build/qsim/.git ; then
      echo "Looks like QSim is a submodule of some other repo."\
           "\`nix-build\` is unable to detect its version, unfortunately."\
           "Please checkout QSim as a normal Git repository"\
           "and retry." >&2
      exit 1
    fi
  '';

  buildInputs = [ setuptools_scm ];

  checkInputs = [ pytest pytest-mypy hypothesis ];

  propagatedBuildInputs = [ numpy ];

  checkPhase = ''
    pytest
  '';

  inherit doCheck;
}


