from dataclasses import dataclass
import random

N_NODES = 4
OPS = [
    "none",
    "skip_connect",
    "nor_conv_1x1",
    "nor_conv_3x3",
    "avg_pool_3x3",
]

@dataclass
class ArchConfig:

    edges: list[list]
    n_nodes: int = 4

    def to_arch_str(self):
        expr = ['|']*self.n_nodes
        for frm, to, ops in self.edges:
            expr[to] += f'{ops}~{frm}|'

        return "+".join(expr[1:])

    @classmethod
    def from_arch_str(cls, str):
        edges = []
        groups = str.split('+')
        for to, group in enumerate(groups, start = 1):
            items = group.strip('|').split('|')
            for item in items:
                ops, frm = item.split('~')
                edges.append([int(frm), to, ops])


        return cls(edges, len(groups) + 1)



def random_arch(n_nodes):
    edges = []
    for i in range(1, n_nodes):
        for j in range(i):
            edges.append([j, i, random.choice(OPS)])

    return ArchConfig(edges, n_nodes)



if __name__ == "__main__":
    # from nats_bench import create

    # api = create(None, "tss", verbose=False, fast_mode=True)
    # for i in range(10):
    #     arch = random_arch(N_NODES)
    #     idx = api.query_index_by_arch(arch.to_arch_str())

    #     assert idx >= 0, f"invalid arch string: {arch.to_arch_str()}"
    #     #print(f"{i}: idx={idx}  {arch.to_arch_str()}")
    # #print("All 10 arch strings resolved to valid indices.")
    ok = 0
    for i in range(20):
        a = random_arch(N_NODES)

        if ArchConfig.from_arch_str(a.to_arch_str())==a:
            ok += 1


    print(f"round-trip: {ok}/20")

