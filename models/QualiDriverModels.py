class InitCommandContext:
    def __init__(self, connectivity, resource):
        self.connectivity = connectivity  # Connectivity details that can help connect to the APIs
        """:type : ConnectivityContext"""
        self.resource = resource  # The details of the resource using the driver
        """:type : ResourceContextDetails"""


class ResourceCommandContext:
    def __init__(self, connectivity, resource, reservation, connectors):
        self.connectivity = connectivity  # Connectivity details that can help connect to the APIs
        """:type : ConnectivityContext"""
        self.resource = resource  # The details of the resource using the driver
        """:type : ResourceContextDetails"""
        self.reservation = reservation  # The details of the reservation
        """:type : ReservationContextDetails"""
        self.connectors = connectors  # The list of visual connectors and routes that are connected to the resource (the resource will be considered as the source end point)
        """:type : list[Connector]"""


class ConnectivityContext:
    def __init__(self, server_address, cloudshell_api_port, quali_api_port, admin_auth_token):
        self.server_address = server_address  # The address of the Quali server
        """:type : str"""
        self.cloudshell_api_port = cloudshell_api_port  # the port of the TestShell API
        """:type : str"""
        self.quali_api_port = quali_api_port  # The port of the Quali API
        """:type : str"""
        self.admin_auth_token = admin_auth_token  # security token
        """:type : str"""


class ResourceContextDetails:
    def __init__(self, id, name, fullname, type, address, model, family, description, attributes, appdata_json,
                 vmdata_json):
        self.id = id  # The identifier of the resource / service / app - consistent value that can't be changed / renamed by the user
        """:type : str"""
        self.name = name  # The name of the resource
        """:type : str"""
        self.fullname = fullname  # The full name (path) of the resource
        """:type : str"""
        self.type = type  # The type of the resource  (Service, App, Resource)
        """:type : str"""
        self.address = address  # The IP address of the resource
        """:type : str"""
        self.model = model  # The resource model
        """:type : str"""
        self.family = family  # The resource family
        """:type : str"""
        self.description = description  # The resource description
        """:type : str"""
        self.attributes = attributes  # A dictionary that contains the resource attributes (name, value)
        """:type : dict[str,str]"""
        self.appdata_json = appdata_json;  # In case of an app, a json serialized object that contains the app details, including the selected deployment and installation configuration
        """:type : str"""
        self.vmdata_json = vmdata_json;  # In case of a virtual machine (deployed app), a json serialized object that contains the host details
        """:type : str"""


class Connector:
    def __init__(self, source, target, target_family, target_model, target_type, target_attributes, direction, alias,
                 attributes, connection_type):
        self.source = source  # The name of the source resource (end point)
        """:type : str"""
        self.target = target  # The name of the target resource (end point)
        """:type : str"""
        self.target_family = target_family  # The family of the target resource
        """:type : str"""
        self.target_model = target_model  # The model of the target resource
        """:type : str"""
        self.target_type = target_type  # The type of the target resource  (Service, App, Resource)
        """:type : str"""
        self.target_attributes = target_attributes  # A dictionary with the target resource attributes (name, value)
        """:type : dict[str,str]"""
        self.direction = direction  # The direction of the connection: Uni, Bi
        """:type : str"""
        self.alias = alias  # The connection alias
        """:type : str"""
        self.attributes = attributes  # The dictionary that includes the connection attributes (name, value)
        """:type : dict[str,str]"""
        self.connection_type = connection_type  # The type of the connection: Route, Visual Connector, Physical
        """:type : str"""


class ReservationContextDetails:
    def __init__(self, environment_name, environment_path, domain, description, owner_user, owner_email,
                 reservation_id):
        self.reservation_id = reservation_id  # The unique identifier of the reservation
        """:type : str"""
        self.environment_name = environment_name  # The name of the environment
        """:type : str"""
        self.environment_path = environment_path  # The full path of the environment
        """:type : str"""
        self.domain = domain  # The reservation domain
        """:type : str"""
        self.description = description  # The reservation description
        """:type : str"""
        self.owner_user = owner_user  # the owner of the reservation
        """:type : str"""
        self.owner_email = owner_email  # the email of the owner of the reservation
        """:type : str"""


class CancellationContext:
    def __init__(self):
        self.is_cancelled = False
        """:type : bool"""


class AutoLoadCommandContext:
    def __init__(self, connectivity, resource):
        self.connectivity = connectivity  # Connectivity details that can help connect to the APIs
        """:type : ConnectivityContext"""
        self.resource = resource  # The details of the resource using the driver
        """:type : ResourceContextDetails"""


class AutoLoadDetails:
    def __init__(self, resources, attributes):
        self.resources = resources  # the list of resources (root and sub) that were discovered
        """:type : list[AutoLoadResource]"""
        self.attributes = attributes  # the list of attributes for the resources
        """:type : list[AutoLoadAttribute]"""


class AutoLoadResource:
    def __init__(self, model, name, relative_address, unique_identifier=None):
        self.model = model
        """:type : str"""
        self.name = name
        """:type : str"""
        self.relative_address = relative_address
        """:type : str"""
        self.unique_identifier = unique_identifier
        """:type : str"""


class AutoLoadAttribute:
    def __init__(self, relative_address, attribute_name, attribute_value):
        self.relative_address = relative_address
        """:type : str"""
        self.attribute_name = attribute_name
        """:type : str"""
        self.attribute_value = attribute_value
        """:type : str"""


class ResourceRemoteCommandContext:
    def __init__(self, connectivity, resource, remote_reservation, ports, remote_endpoints):
        self.connectivity = connectivity  # Connectivity details that can help connect to the APIs
        """:type : ConnectivityContext"""
        self.resource = resource  # The details of the resource using the driver
        """:type : ResourceContextDetails"""
        self.remote_reservation = remote_reservation  # The details of the remote reservation
        """:type : ReservationContextDetails"""
        self.remote_endpoints = remote_endpoints
        """:type : list[ResourceContextDetails]"""
