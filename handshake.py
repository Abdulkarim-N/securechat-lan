from cryptography.hazmat.primitives.serialization import ParameterFormat

def serialize_parameters(parameters):
    return parameters.parameter_bytes(Encoding.DER, ParameterFormat.PKCS3)

def deserialize_parameters(data):
    from cryptography.hazmat.primitives.asymmetric.dh import DHParameterNumbers
    from cryptography.hazmat.primitives.serialization import load_der_parameters
    return load_der_parameters(data)