"""v1 choice: as_combined -- it gives the model both the architecture's
structure and its measured accuracy in one block, so the model can reason
about which edges/ops correlate with performance instead of pattern-matching
structure alone.
"""

from search_space import ArchConfig, random_arch
from nats_bench import create


N_NODES = 4


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

def as_combined(arch, accuracy):
    adjacency = as_adjacency(arch)
    return f"{adjacency}\nAccuracy: {accuracy:.2f}%"



def main():
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