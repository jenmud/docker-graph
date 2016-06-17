"""
Setup the environment by parsing the command line options and staring
a ruruki http server.
"""
import argparse
import docker
import logging
import os
from ruruki_eye.server import run
from docker_graph.scrape import GRAPH
from docker_graph.scrape import scrape_image


__all__ = ["get_image_detail"]


def scrape(image=None):
    """
    Inspect the image and scrape the details.

    :param image: Image that you are scraping. If omitted then all images
        will be scrapped.
    :type image: :class:`str` or :obj:`None`
    :returns: Image inspect detail.
    :rtype: :class:`dict`
    """
    details = []
    client = docker.Client()
    for detail in client.images(name=image, all=True):
        scrape_image(image, detail)
        details.append(detail)
    return details


def parse_arguments():
    """
    Parse the command line arguments.

    :returns: All the command line arguments.
    :rtype: :class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="Docker image dependency grapher."
    )

    # parser.add_argument(
    #     "--image",
    #     nargs="+",
    #     type=scrape,
    #     help="Build dependency graph for given image.",
    # )

    parser.add_argument(
        "--runserver",
        action="store_true",
        help="Start a ruruki http server.",
    )

    parser.add_argument(
        "--address",
        default="0.0.0.0",
        help="Address to start the web server on. (default: %(default)s)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help=(
            "Port number that the web server will accept connections on. "
            "(default: %(default)d)"
        ),
    )

    return parser.parse_args()


def main():
    """
    Entry point.
    """
    logging.basicConfig(level=logging.INFO)
    namespace = parse_arguments()
    scrape()

    if namespace.runserver is True:
        run(namespace.address, namespace.port, False, GRAPH)
