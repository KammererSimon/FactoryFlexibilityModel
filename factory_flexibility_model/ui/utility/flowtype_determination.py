# This file contains all functions required to enable the gui to automatically keep track of the flowtypes of components within the layout and to automatically assign flowtypes when new connections are being created


def set_component_flowtype(blueprint, component_key: str, flowtype):
    """
    This function takes a blueprint of a factory, a key to one of the components within the factory and a fowtype object.
    If the component referenced by the key has an internal flowtype it is set to the given flowtype.
    Additionally all connections from and to the component are checked, if they match the new assigned flowtype.
    If they don't, the set_connection_flowtype-method is called to assign the new flowtype to them as well.
    :param blueprint: [Blueprint.Blueprint] The current blueprint object of the gui session that this function is being called from
    :param component_key: [str] Unique identifier key of one of the components within the blueprint. It is expected to be withing blueprint.components.keys()
    :param flowtype: [Flowtype.Flowtype] Expecpected to be a valid factory model Flowtype object
    """

    # abort if the component is a converter
    if blueprint.components[component_key]["type"] == "converter":
        return

    # set the flowtype of the given component as the given flowtype
    blueprint.components[component_key]["flowtype"] = flowtype

    # iterate over all connections of the component to check if there are more places where the new flowtype needs to be set...
    for connection in blueprint.connections.values():
        if connection["from"] == component_key or connection["to"] == component_key:
            set_connection_flowtype(blueprint, connection["key"], flowtype)


def set_connection_flowtype(blueprint, connection_key, flowtype):
    """
    This function takes a blueprint of a factory, a key to one of the connections within the factory and a flowtype object.
    If the referenced connection already has the specified flowtype this function does nothing.
    Otherwise the flowtype of the adressed connection will be changed to the given flowtype within the blueprint
    If the flowtype of the conenction has been changed, both origin and destination component of the connection are checked, if they have a matching flowtype.
    If either of them hasn't, the set_component_flowtype() method is called on them with the new flowtype.
    :param blueprint: [Blueprint.Blueprint] The current blueprint object of the gui session that this function is being called from
    :param connection_key: [str] Unique identifier key of one of the connections within the blueprint. It is expected to be withing blueprint.connections.keys()
    :param flowtype: [Flowtype.Flowtype] Expecpected to be a valid factory model Flowtype object
    """

    if not blueprint.connections[connection_key]["flowtype"].key == flowtype.key:
        # set the flowtype of the given connection as the given flowtype
        blueprint.connections[connection_key]["flowtype"] = flowtype

        # continue with setting the flowtype of the other end of the connection
        if (
            not blueprint.components[blueprint.connections[connection_key]["from"]][
                "key"
            ]
            == flowtype.key
        ):
            set_component_flowtype(
                blueprint, blueprint.connections[connection_key]["from"], flowtype
            )

        if (
            not blueprint.components[blueprint.connections[connection_key]["to"]]["key"]
            == flowtype.key
        ):
            set_component_flowtype(
                blueprint, blueprint.connections[connection_key]["to"], flowtype
            )
