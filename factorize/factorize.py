import click
import enum
import itertools
import json
from collections import defaultdict
from copy import copy
from dataclasses import dataclass
from dataclasses import field
from graphviz import Digraph
from math import ceil
from pprint import pprint
from typing import List
from typing import Mapping
from typing import Optional


class RecipeSpecType(click.ParamType):
    """Recipe name:count CLI option custom type"""

    name = 'recipe_spec'

    def convert(self, value, param, ctx):
        try:
            recipe, rate = value.split(':')
            return (recipe, int(rate))
        except (TypeError, IndexError, ValueError):
            raise self.fail('spec must be in format "recipe-name:items_per_minute", got "{}"'.format(value))


@enum.unique
class RecipeCategory(enum.Enum):

    ADVANCED_CRAFTING = 'advanced-crafting'
    CENTRIFUGING = 'centrifuging'
    CHEMISTRY = 'chemistry'
    CRAFTING = 'crafting'
    CRAFTING_WITH_FLUID = 'crafting-with-fluid'
    OIL_PROCESSING = 'oil-processing'
    RESOURCE = 'resource'
    ROCKET_BUILDING = 'rocket-building'
    SMELTING = 'smelting'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_  # pylint: disable=no-member

    @classmethod
    def get_value_key(cls, value):
        return cls._value2member_map_[value]  # pylint: disable=no-member


@enum.unique
class PowerType(enum.IntEnum):

    BURNER = 0
    ELECTRIC = 1


@dataclass
class CraftingMachine:

    name: str
    crafting_speed: float
    power_type: PowerType

    def __lt__(self, other):
        if self.crafting_speed == other.crafting_speed:
            return self.power_type.value < other.power_type.value
        return self.crafting_speed < other.crafting_speed


@dataclass
class Ingredient:

    name: str
    count: int


@dataclass
class Recipe:

    name: str
    time: float
    result_count: int
    category: RecipeCategory
    ingredients: List[Ingredient] = field(default_factory=list)


@dataclass
class Context:

    recipes: Mapping[str, Recipe]
    draw: bool = False


RECIPE_SPEC = RecipeSpecType()


FURNACES = (
    CraftingMachine('stone-furnace', 1.0, PowerType.BURNER),
    CraftingMachine('steel-furnace', 2.0, PowerType.BURNER),
    CraftingMachine('electric-furnace', 2.0, PowerType.ELECTRIC),
)

ASSEMBLY_MACHINES = (
    CraftingMachine('assembly-machine-1', 0.5, PowerType.ELECTRIC),
    CraftingMachine('assembly-machine-2', 0.75, PowerType.ELECTRIC),
    CraftingMachine('assembly-machine-3', 1.25, PowerType.ELECTRIC),
)

REFINERIES = (
    CraftingMachine('oil-refinery', 1.0, PowerType.ELECTRIC),
)

PLANTS = (
    CraftingMachine('chemical-plant', 1.0, PowerType.ELECTRIC),
)

CRAFTING_MACHINES = {
    RecipeCategory.SMELTING: FURNACES,
    RecipeCategory.ADVANCED_CRAFTING: ASSEMBLY_MACHINES,
    RecipeCategory.CRAFTING: ASSEMBLY_MACHINES,
    RecipeCategory.CRAFTING_WITH_FLUID: ASSEMBLY_MACHINES[1:],
    RecipeCategory.CHEMISTRY: PLANTS,
    RecipeCategory.OIL_PROCESSING: REFINERIES,
}


SCIENCE_PACKS = (
    'automation-science-pack',
    'logistic-science-pack',
    'production-science-pack',
    'utility-science-pack',
    'chemical-science-pack',
    'military-science-pack',
)


def load_data():
    data_file = 'dump/data.json'
    with open(data_file) as fp:
        return fp.read()


def parse_data(raw_data):
    items = json.loads(raw_data)
    recipes = {}
    ingredients = set()

    for item in items:
        if not item['type'] == 'recipe':
            continue

        if 'normal' in item and 'expensive' in item:
            info = item['normal']
            time = info.get('energy_required', 0.5)
            ing_list = item['normal']['ingredients']
        else:
            time = item.get('energy_required', 0.5)
            ing_list = item.get('ingredients', [])

        if 'results' in item:
            result = None
            for res in item['results']:
                if isinstance(res, dict) and res['name'] == item['name']:
                    result = res
                    break
            if result is not None:
                result_count = result['amount']
        else:
            result_count = item.get('result_count', 1)

        deps = []
        for ing in ing_list:
            if isinstance(ing, list):
                deps.append(Ingredient(name=ing[0], count=ing[1]))
            else:
                deps.append(Ingredient(name=ing['name'], count=ing['amount']))

        ingredients.update(ing.name for ing in deps)

        recipes[item['name']] = Recipe(
            name=item['name'],
            time=float(time),
            ingredients=tuple(deps),
            result_count=result_count,
            category=RecipeCategory.get_value_key(item.get('category', 'crafting')))

    # add raw materials as recipes with no ingredients
    for name in ingredients - set(recipes.keys()):
        recipes[name] = Recipe(
            name=name,
            time=0.0,
            result_count=1,
            category=RecipeCategory.RESOURCE)

    for name, recipe in recipes.items():
        # check whether all recipes have their ingredients also defined as
        # recipe
        if not all(ing.name in recipes for ing in recipe.ingredients):
            raise ValueError(f'"{name}" does not have all ingredients defined')

    return recipes


def calc_required_factories(recipe: Recipe, speed_multiplier: float, items_per_minute: float) -> float:
    """
    Calculate the number of factories (crafting machines) required to produce
    the given amount of items per minute, as defined by the recipe.
    """

    ipm = 60.0 / (recipe.time / (recipe.result_count * speed_multiplier))
    return ceil(items_per_minute / ipm)


def calc_cycles_per_minute(recipe: Recipe, n_factories) -> float:
    """
    Calculate the number of production cycles per minute for a given recipe by
    a given number of factories.
    """
    return ceil((60.0 / recipe.time) * n_factories)


def get_best_machine(recipe: Recipe) -> Optional[CraftingMachine]:
    if recipe.category is not RecipeCategory.RESOURCE:
        return CRAFTING_MACHINES[recipe.category][-1]
    return None


def get_recipe_chain(data, recipe_name: str, prod_rate: float):
    chain = []
    deps = [Ingredient(recipe_name, prod_rate)]

    while deps:
        ing = deps.pop(0)
        recipe = data[ing.name]

        chain.append(ing)

        machine = get_best_machine(recipe)
        if machine is None:
            continue

        factories = calc_required_factories(recipe, machine.crafting_speed, ing.count)
        cycles = calc_cycles_per_minute(recipe, factories)

        for ing in recipe.ingredients:
            ing = copy(ing)
            ing.count *= cycles
            deps.append(ing)

    return chain


def draw_chain_graph(data, ingredients):
    ingredient_ids = {}
    for ing in ingredients:
        if ing not in ingredient_ids:
            ingredient_ids[ing] = len(ingredient_ids)

    dot = Digraph(comment='Megafactory')
    dot.attr(engine='neato')
    dot.attr(overlap='false')
    dot.attr(splines='ortho')
    dot.attr(ranksep='1.5')

    for ing_name, ing_id in ingredient_ids.items():
        recipe = data[ing_name]
        machine = get_best_machine(recipe)
        if machine is not None:
            factories = calc_required_factories(
                recipe, machine.crafting_speed, ingredients[ing_name])
            factory_info = f'{factories} {machine.name.replace("-", " ")}'
        else:
            factory_info = ''

        if ing_name in SCIENCE_PACKS:
            fillcolor = 'yellow'
        else:
            fillcolor = 'white'

        dot.node(
            str(ing_id),
            '{}\n{}'.format(
                ing_name.replace('-', ' '),
                factory_info),
            shape='rectangle',
            style='filled',
            fillcolor=fillcolor)

    edges = set()
    for ing in ingredients:
        recipe = data[ing]
        for dep in recipe.ingredients:
            if dep.name in ingredient_ids:
                edge = (ingredient_ids[dep.name], ingredient_ids[ing])
                edges.add(edge)

    for u, v in edges:
        dot.edge(str(u), str(v))

    dot.render('megafactory', format='png')


@click.group()
@click.pass_context
@click.option('--draw', type=bool, is_flag=True,
    help='Draw the factory graph to a PNG file')
def cli(ctx, draw):
    """Factorio utility toolset.

    Calculates the factory configuration for producing given recipes at desired
    rates, along with their dependencies, useful for planning and construction
    of efficient production chains."""
    ctx.obj.draw = draw


@cli.command()
@click.pass_context
@click.argument('recipe_spec', nargs=-1, type=RECIPE_SPEC)
def factories(ctx, recipe_spec: [str, float]):
    """Factories required for producing recipes at given rates.

    RECIPE_SPEC is a space-separated list of recipe-name:items_per_minute
    specifiers, for example:

        factorize.py factories explosive-cannon-shell:10 firearm-magazine:50

    will print a table of required factories necessary to produce 10 cannon
    shells and 50 firearm magazines per minute, along with the crafting machines
    necessary for producing the required intermediary products, such as furnaces
    and chemical plantes.
    """
    data = ctx.obj.recipes

    chain = list(itertools.chain.from_iterable(
        get_recipe_chain(data, recipe, rate) for recipe, rate in recipe_spec))

    ingredients = defaultdict(int)

    for ing in chain:
        ingredients[ing.name] += ing.count

    machines = {}
    for ing, count in ingredients.items():
        recipe = data[ing]

        machine = get_best_machine(recipe)
        if machine is None:
            machines[ing] = (0, None)
        else:
            machines[ing] = (
                calc_required_factories(recipe, machine.crafting_speed, count),
                machine)

    names_by_count = sorted(ingredients.keys(), key=lambda k: ingredients[k])

    name_col_size = max(len(ing.name) for ing in chain) + 2

    header = f'{{:>7s}} {{:{name_col_size}}}      {{}}'.format('IPS', 'RECIPE', 'CRAFTING MACHINE')
    print(header)

    for name in names_by_count:
        ing_count = ingredients[name]
        machine_count, machine = machines[name]
        if machine is None:
            continue

        machine_info = f'{machine_count:>5d} {" ".join(machine.name.split("-"))}'
        print(f'{ing_count:>7d} {" ".join(name.split("-")):<{name_col_size}}->{machine_info}')

    if ctx.obj.draw:
        draw_chain_graph(data, ingredients)


@cli.command()
@click.pass_context
@click.argument('spm', type=int)
@click.option('--no-military', type=bool, is_flag=True,
    help='Exclude military science packs')
def science(ctx, spm: int, no_military: bool):
    """Factories required for producing science packs at given rate."""
    pack_names = set(SCIENCE_PACKS)
    if no_military:
        pack_names.remove('military-science-pack')

    ctx.invoke(
        factories,
        recipe_spec=[(pack, spm) for pack in pack_names])


if __name__ == '__main__':
    data = load_data()
    recipes = parse_data(data)
    context = Context(recipes)
    cli(obj=context)  # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
