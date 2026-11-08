

def lookup(api, idx):
    valid = api.get_more_info(idx, 'cifar10-valid', hp='200', is_random=False)['valid-accuracy']
    test = api.get_more_info(idx, 'cifar10', hp='200', is_random=False)['test-accuracy']
    api.clear_params(idx)
    return valid, test