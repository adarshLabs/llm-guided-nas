"""v1 choice: as_combined -- it gives the model both the architecture's
structure and its measured accuracy in one block, so the model can reason
about which edges/ops correlate with performance instead of pattern-matching
structure alone.

Accuracy goes in search-loop prompts because it is the feedback signal,
and never in a held-out evaluation prompt.
"""

from search_space import ArchConfig, random_arch, OPS, N_NODES



OP_PHRASE = {
    "none":         "no connection",
    "skip_connect": "a skip connection",
    "nor_conv_1x1": "a 1x1 convolution",
    "nor_conv_3x3": "a 3x3 convolution",
    "avg_pool_3x3": "3x3 average pooling",
}


def as_adjacency(arch):
    adj = []
    for frm, to, ops in arch.edges:
        adj.append(f"{frm} -> {to} : {ops}")

    return "\n".join(adj)

def as_table(arch):
    table = [f"|{'From':^7}|{'To':^7}|{'Operation':^15}|", f"|{'-'*7}|{'-'*7}|{'-'*15}|"]
    for frm, to, ops in arch.edges:
        table.append(f"|{frm:^7}|{to:^7}|{ops:^15}|")

    return "\n".join(table)


def as_nats(arch):
    return arch.to_arch_str()


def as_prose(arch):
    by_to = {}
    for frm, to, op in arch.edges:
        src = "the input" if frm==0 else f"node {frm}"
        by_to.setdefault(to, []).append(f"{OP_PHRASE[op]} from {src}")

    out = []
    for to, parts in sorted(by_to.items()):
        if len(parts)>1:
            parts = [ ", ".join(parts[:-1]), parts[-1]]
        out.append(f"Node {to} takes {' and '.join(parts)}.")

    return " ".join(out)

def as_combined(arch, accuracy, fmt=as_adjacency):
    return f"{fmt(arch)}\nCIFAR-10 test accuracy (hp=200): {accuracy:.2f}%"

def main():
    from nats_bench import create
    api = create(None, 'tss', verbose=False, fast_mode=True)
    for i in range(5):
        arch = random_arch(N_NODES)
        arch_str = arch.to_arch_str()

        idx = api.query_index_by_arch(arch_str)

        assert idx>=0, "Correct String format"

        info = api.get_more_info(idx, 'cifar10', hp='200', is_random=False)
        test_accuracy = info["test-accuracy"]
        print(f"\n\nArchitecture {i+1}: ")
        print(f"\nAdjacency: \n{as_adjacency(arch)}")
        print(f"\nTable: \n{as_table(arch)}")
        print(f"\nCombined: \n{as_combined(arch, test_accuracy)}")
        api.clear_params(idx)





if __name__=="__main__":
    main()