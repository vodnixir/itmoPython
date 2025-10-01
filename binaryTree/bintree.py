from collections import defaultdict


class BinTree:
    def __init__(self):
        pass

    def get_left(self, root):
        return root * 3

    def get_right(self, root):
        return root + 4

    def parser1(self, tree, indent=0):
        for root, c in tree.items():
            print(" " * indent + str(root))  # выводим корень
            for ch in c:
                if isinstance(ch, dict):
                    self.parser1(ch, indent + 4)  # рекурсивный спуск
                else:
                    print(" " * (indent + 4) + str(ch))  # лист

    def parser2(self, tree):
        """
        Выводит дерево по горизонтальным уровням (level-order).
        Формат входа такой же, как у parser1: {root: [left, right]},
        где left/right — либо dict с тем же форматом, либо число-лист.
        """
        levels = defaultdict(list)

        def gather(node, depth):
            # узел может быть dict, множеством {root} или просто числом
            if isinstance(node, dict):
                for r, children in node.items():
                    levels[depth].append(r)
                    # ожидаем ровно два потомка в списке
                    for ch in children:
                        gather(ch, depth + 1)
            elif isinstance(node, set):
                # base-case из _alg: {root}
                for v in node:
                    levels[depth].append(v)
            else:
                # лист (число)
                levels[depth].append(node)

        gather(tree, 0)

        # вывод строками по уровням
        for d in sorted(levels.keys()):
            print(f"Level {d}: " + " ".join(map(str, levels[d])))

    def _alg(self, height, root):
        if height > 1:
            return {root: [self._alg(height - 1, self.get_left(root)), self._alg(height - 1, self.get_right(root))]}
        if height == 1:
            return {root: [self.get_left(root), self.get_right(root)]}
        else:
            return {root}

    def gen_bin_tree(self, height, root):
        res = self._alg(height - 1, root)
        self.parser2(res)


b = BinTree()
b.gen_bin_tree(10, 3)
