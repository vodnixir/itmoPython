import timeit
from collections import defaultdict
import matplotlib.pyplot as plt


class BinTree:
    """
    Класс для генерации и вывода бинарного дерева.
    """

    def __init__(self):
        """Создаёт объект BinTree (без параметров)."""
        pass

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

    def _alg(self, height, root, left=lambda x: x * 3, right=lambda x: x + 4):
        """
        Рекурсивно строит дерево заданной высоты.

        Args:
            height (int): глубина дерева.
            root (int): значение корневого узла.

        Returns:
            dict: дерево в виде вложенных словарей.
        """

        if height > 1:
            return {root: [self._alg(height - 1, left(root)),
                           self._alg(height - 1, right(root))]}
        if height == 1:
            return {root: [left(root), right(root)]}
        else:
            return {root}

    def _alg_iter(self, height, root, left=lambda x: x * 3, right=lambda x: x + 4):
        """
        Итеративное построение структуры дерева в формате:
        {root: [левое_поддерево, правое_поддерево]} / {root} / {root:[left_val, right_val]}
        Точная эквивалентность поведению _alg из рекурсивной версии.
        """
        if height <= 0:
            return {root}
        if height == 1:
            return {root: [left(root), right(root)]}
        frames = [{'root': root, 'h': height, 'state': 0}]
        built = []

        while frames:
            f = frames.pop()
            r, h, state = f['root'], f['h'], f['state']

            if h <= 0:
                built.append({r})
                continue

            if h == 1:
                built.append({r: [left(r), right(r)]})
                continue

            if state == 0:
                f['state'] = 1
                frames.append(f)
                right_r = right(r)
                left_r = left(r)
                frames.append({'root': right_r, 'h': h - 1, 'state': 0})
                frames.append({'root': left_r, 'h': h - 1, 'state': 0})

            else:
                right_sub = built.pop()
                left_sub = built.pop()
                built.append({r: [left_sub, right_sub]})
        return built[-1]



    def test(self, height, root, use_parser1=False, *, max_nodes=200_000, left=lambda x: x * 3, right=lambda x: x + 4):
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
            l = left(root)
            r = right(root)
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

    def gen_bin_tree(self, height: int, root: int, use_parser1: bool = False, *, algo: str = "iter", left=lambda x: x * 3, right=lambda x: x + 4):
        """
        Генерация бинарного дерева и вывод его в консоль.

        Args:
            height (int): глубина дерева.
            root (int): корневое значение.
            use_parser1 (bool): если True — вывод через parser1 (отступами);
                                иначе parser2 (уровнями).
            algo (str): выбор алгоритма построения:
                        "iter" — использовать _alg_iter (по умолчанию, итеративный, без рекурсии),
                        "rec"  — использовать _alg (рекурсивный).

        Output:
            Печатает дерево в консоль в выбранном формате.
        """
        self.test(height, root, use_parser1)
        if algo in ("iter", "i"):
            builder = self._alg_iter
        elif algo in ("rec", "r"):
            builder = self._alg
        else:
            raise ValueError("Неверный параметр algo: ожидается 'iter' или 'rec'.")
        res = builder(height - 1, root, left=left, right=right)
        (self.parser1 if use_parser1 else self.parser2)(res)


b = BinTree()
# b.gen_bin_tree(4, 3)
# print(timeit.timeit(stmt='b._alg(4, 3)', setup='b=BinTree()', number=1))
# print(timeit.timeit(lambda: b._alg(6, 3), number=1000))
# print(timeit.timeit(lambda: b._alg_iter(6, 3), number=1000))

t1, t2 = [], []
for i in range(10):
    t1.append(timeit.timeit(lambda: b._alg(i, 3), number = 1))
    t2.append(timeit.timeit(lambda: b._alg_iter(i, 3), number = 1))
y = range(10)
print(1)
plt.plot(y, t1, label='Рекурсивный алгоритм')
plt.plot(y, t2, label='Итеративный алгоритм')
plt.xlabel("Высота дерева")
plt.ylabel("Время выполнения")
plt.legend()
plt.show()
# Вывод: рекурсивная функция является более эффектиной по сравнению с итеративной, изначально результаты мало рознятся, но в дальнейшем разница становится только больше
