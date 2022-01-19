#!/bin/sh
# flatpak-pip-generator --requirements-file=requirements.txt
flatpak-builder build io.github.vegad.vnotes.yml --force-clean --repo=repo
flatpak build-bundle repo vnotes.flatpak io.github.vegad.vnotes


flags()
{
    while test $# -gt 0
    do
        case "$1" in
        (-i|--install)
            shift
            flatpak remove --force-remove --delete-data --noninteractive -y vnotes
            flatpak-builder --user --install --force-clean build io.github.vegad.vnotes.yml
            shift;;
        (*) usage;;
        esac
    done
}
