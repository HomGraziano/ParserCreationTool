def parse_locations(text):
    result = {}
    lines = text.strip().split('\n')
    for line in lines:
        try:
            address, id_str = line.split(':', 1)
            result[address.strip().lower()] = int(id_str.strip())
        except ValueError:
            continue
    return result


def chargesloop(number_of_charges):
    return [
        {
            "id": str(i + 1),
            "amount": 0,
            "quantity": "1",
            "only_if_added": True
        } for i in range(number_of_charges)
    ]
