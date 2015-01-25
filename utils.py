
import netifaces


def get_potential_ips():
    """Return potential IP addresses under which this computer might be
    reachable.
    """
    potential_ips = []
    for name in netifaces.interfaces():
        interface = netifaces.ifaddresses(name).get(netifaces.AF_INET)
        if interface:
            ptential_ip = interface[0]['addr']
            if ptential_ip != '127.0.0.1':
                potential_ips.append(ptential_ip)
    return potential_ips
