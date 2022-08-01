#!/bin/sh
# flatpak-pip-generator --requirements-file=requirements.txt
rm -rf repo
mkdir repo
flatpak-builder build io.github.vegad.vnotes.yml --force-clean --repo=repo
flatpak build-bundle repo vnotes.flatpak io.github.vegad.vnotes

if [ "$1" = "-i" ] || [ "$1" = "--install" ]
then
  flatpak remove --force-remove --delete-data --noninteractive -y vnotes
  flatpak-builder --user --install --force-clean build "io.github.vegad.vnotes.yml"
fi

if [ "$2" = "-r" ] || [ "$2" = "--run" ]
then
  flatpak run io.github.vegad.vnotes
fi