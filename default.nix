{
  pkgs,
  ...
}:
pkgs.writeShellApplication {
  name = "yt-subs";
  runtimeInputs = with pkgs; [
    yt-dlp
    ollama
    fzf
  ];
  text = builtins.readFile ./yt-subs.sh;
}
