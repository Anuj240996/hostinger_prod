import subprocess

# Read the requirements file
with open('reqs_now.txt', 'r') as file:
    packages = file.readlines()

# Strip whitespace characters like newline
packages = [pkg.strip() for pkg in packages]

# Function to check if a package has dependencies
def has_dependencies(package):
    result = subprocess.run(['pip', 'show', package], capture_output=True, text=True)
    # If "Requires" is in the output, it means the package has dependencies
    if "Requires" in result.stdout:
        return True
    return False

# Uninstall packages without dependencies
for package in packages:
    if not has_dependencies(package):
        print(f"Uninstalling {package} as it has no dependencies.")
        subprocess.run(['pip', 'uninstall', '-y', package])
    else:
        print(f"{package} has dependencies, skipping uninstall.")
