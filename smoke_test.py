from nats_bench import create

api = create(None, 'tss', verbose=False, fast_mode=True)

for dset in ['cifar10', 'cifar100', 'ImageNet16-120']:
    idx, best_accuracy = -1, -1.0
    for i in range(len(api)):
        info = api.get_more_info(i, dset, hp='200', is_random=False)

        if info['test-accuracy']> best_accuracy:
            best_accuracy = info['test-accuracy']
            idx = i
        api.clear_params(idx) 
    print(f"{dset:16s} best arch #{idx}    test {best_accuracy:.2f}%")
