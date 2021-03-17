import os


def get_environment_variable_value(variable_name: str, default_value: str) -> str:
    """
    Returns an environment variable's value or default value if the app is started locally
    """
    value = os.environ.get(variable_name)

    if value is None:
        if __name__ == '__main__':
            print(f'Getting default value for env variable {variable_name}')
            value = default_value
        else:
            raise EnvironmentError(f'No environment variable {variable_name}')

    return value