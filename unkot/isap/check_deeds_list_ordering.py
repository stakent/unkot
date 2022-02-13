def check_deeds_list_ordering(deeds):
    for n in range(0, len(deeds)):
        if n == len(deeds) - 1:
            break
        current = deeds[n]
        previous = deeds[n + 1]
        if current.change_date <= previous.change_date:
            if (
                current.change_date == previous.change_date
                and current.address <= previous.address
            ):
                return
            msg = f'deeds in bad order n: { n }\n'
            msg += f'current  { current.address } { current.change_date }\n'
            msg += f'previous { previous.address } { previous.change_date }'
            raise ValueError(msg)
