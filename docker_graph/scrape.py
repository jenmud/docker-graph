import docker
import logging
import json
from ruruki import graphs
from ruruki_eye import server


__all__ = ["GRAPH", "scrape_image"]


GRAPH = graphs.Graph()
GRAPH.add_vertex_constraint("IMAGE", "id")
GRAPH.add_vertex_constraint("CONTAINER", "id")
GRAPH.add_vertex_constraint("AUTHOR", "name")
GRAPH.add_vertex_constraint("REPO", "name")
GRAPH.add_vertex_constraint("TAG", "name")
GRAPH.add_vertex_constraint("LAYER", "id")

 # {u'Created': 1451440833,
 #           u'Id': u'sha256:7f6fe0c33fc69148c1f42f3feb3c5ea61a22b1d58cdf06d538f0acb8e0794105',
 #             u'Labels': None,
 #               u'ParentId': u'sha256:51ccae90420f667590a375a7cfd8a9db7313f41226246374f9d74b90ae657a54',
 #                 u'RepoDigests': [u'<none>@<none>'],
 #                   u'RepoTags': [u'<none>:<none>'],
 #                     u'Size': 304990962,
 #                       u'VirtualSize': 304990962},

def scrape_image(name, inspect_detail):
    """
    Scrape information from a inspect dump.

    :param inspect_detail: Docker inspect JSON dump for a image.
    :type inspect_detail: :class:`dict`
    """
    name = name if name else inspect_detail["Id"][:15]
    image_node = GRAPH.get_or_create_vertex(
        "IMAGE",
        name=name,
        id=inspect_detail["Id"],
        created=inspect_detail["Created"],
        size=inspect_detail["Size"],
        virtual_size=inspect_detail["VirtualSize"],
    )

    for repotag in inspect_detail.get("RepoTags", []):
        repo, tag = repotag.split(":", 1)
        repo_node = GRAPH.get_or_create_vertex("REPO", name=repo)

        GRAPH.get_or_create_edge(
            repo_node,
            "HAS-TAG",
            ("TAG", {"name": tag}),
        )

        GRAPH.get_or_create_edge(
            image_node,
            "HAS-REPO",
            repo_node
        )

    parent_id = inspect_detail.get("ParentId")
    if parent_id:
        parent_nodes = GRAPH.get_vertices("IMAGE", id=parent_id)
        if len(parent_nodes) > 1:
            raise ValueError("Can not bind to multiple parent images.")
        elif len(parent_nodes) == 0:
            logging.info(
                "No parent images found for %r, skipping parent linking..",
                name
            )
        else:
            parent_node = parent_nodes.all()[0]
            GRAPH.get_or_create_edge(
                image_node,
                "PARENT",
                parent_node
            )
