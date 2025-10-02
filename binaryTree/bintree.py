from collections import defaultdict


class BinTree:
    """
    Класс для генерации и вывода бинарного дерева.
    """

    def __init__(self):
        """Создаёт объект BinTree (без параметров)."""
        pass

    def get_left(self, root):
        """
        Возвращает значение левого потомка для узла.

        Args:
            root (int): значение текущего узла.

        Returns:
            int: левый потомок (root * 3).
        """
        return root * 3

    def get_right(self, root):
        """
        Возвращает значение правого потомка для узла.

        Args:
            root (int): значение текущего узла.

        Returns:
            int: правый потомок (root + 4).
        """
        return root + 4

    def parser1(self, tree, indent=0):
        """
        Рекурсивный вывод дерева в виде отступов (вертикальный вид).

        Args:
            tree (dict): дерево в формате {root: [left, right]}.
            indent (int): текущий уровень отступа (по умолчанию 0).

        Output:
            Печатает дерево в консоль построчно с отступами.
        """
        for root, c in tree.items():
            print(" " * indent + str(root))
            for ch in c:
                if isinstance(ch, dict):
                    self.parser1(ch, indent + 4)
                else:
                    print(" " * (indent + 4) + str(ch))

    def parser2(self, tree):
        """
        Вывод дерева по уровням (level-order).

        Args:
            tree (dict): дерево в формате {root: [left, right]}.

        Output:
            Печатает в консоль строки вида:
            "Level N: узлы", где N — глубина дерева.
        """
        levels = defaultdict(list)

        def gather(node, depth):
            if isinstance(node, dict):
                for r, children in node.items():
                    levels[depth].append(r)
                    for ch in children:
                        gather(ch, depth + 1)
            elif isinstance(node, set):
                for v in node:
                    levels[depth].append(v)
            else:
                levels[depth].append(node)

        gather(tree, 0)

        for d in sorted(levels.keys()):
            print(f"Level {d}: " + " ".join(map(str, levels[d])))

    def _alg(self, height, root):
        """
        Рекурсивно строит дерево заданной высоты.

        Args:
            height (int): глубина дерева.
            root (int): значение корневого узла.

        Returns:
            dict: дерево в виде вложенных словарей.
        """
        if height > 1:
            return {root: [self._alg(height - 1, self.get_left(root)),
                           self._alg(height - 1, self.get_right(root))]}
        if height == 1:
            return {root: [self.get_left(root), self.get_right(root)]}
        else:
            return {root}

    def test(self, height, root, use_parser1=False, *, max_nodes=200_000):
        """
        Проверяет корректность параметров перед генерацией дерева.

        Args:
            height (int): глубина дерева (≥1).
            root (int): корневое значение.
            use_parser1 (bool): выбор способа вывода (True — parser1, False — parser2).
            max_nodes (int): максимальное число узлов для защиты от переполнения.

        Returns:
            bool: True, если параметры корректны.

        Raises:
            TypeError, ValueError: при некорректных параметрах или слишком большом дереве.
        """
        if not isinstance(height, int):
            raise TypeError("height должен быть int")
        if not isinstance(root, int):
            raise TypeError("root должен быть int")
        if not isinstance(use_parser1, bool):
            raise TypeError("use_parser1 должен быть bool")
        if height < 1:
            raise ValueError("height должен быть ≥ 1")
        try:
            l = self.get_left(root)
            r = self.get_right(root)
        except Exception as e:
            raise ValueError(f"get_left/get_right упали на root={root}: {e}") from e
        if not (isinstance(l, int) and isinstance(r, int)):
            raise TypeError("get_left/get_right должны возвращать int")
        approx_nodes = (1 << height) - 1
        if approx_nodes > max_nodes:
            raise ValueError(
                f"Слишком большое дерево: ~{approx_nodes} узлов > лимита {max_nodes}. "
                f"Уменьшите height или увеличьте max_nodes."
            )
        return True

    def gen_bin_tree(self, height, root, use_parser1: bool = False):
        """
        Генерация бинарного дерева и вывод его в консоль.

        Args:
            height (int): глубина дерева.
            root (int): корневое значение.
            use_parser1 (bool): если True, вывод через parser1 (отступами);
                                иначе parser2 (уровнями).

        Output:
            Печатает дерево в консоль в выбранном формате.
        """
        self.test(height, root, use_parser1)
        res = self._alg(height - 1, root)
        (self.parser1 if use_parser1 else self.parser2)(res)


b = BinTree()
b.gen_bin_tree(6, 2)
b.gen_bin_tree(6, 2, use_parser1=True)  
