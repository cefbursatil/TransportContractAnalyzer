{pkgs}: {
  deps = [
    pkgs.freetype
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
    pkgs.postgresql
    pkgs.glibcLocales
  ];
}
