#!/usr/bin/env python3

"""
CSC2034 evolutionary art coursework solution.

This file provides the three functions imported by the coursework runner:
- initialise()
- draw(solution)
- evolve(population, args)
"""

import random

import evol
from evol.individual import Individual
import PIL.Image
import PIL.ImageDraw


WIDTH = 200
HEIGHT = 200
MAX_SHAPES = 100
MIN_INITIAL_SHAPES = 5
MAX_INITIAL_SHAPES = 10


def clamp(value, low, high):
    return max(low, min(high, value))


def random_shape(detail_mode=False):
    centre_x = random.randint(0, WIDTH - 1)
    centre_y = random.randint(0, HEIGHT - 1)

    if detail_mode:
        if random.random() < 0.65:
            radius = random.randint(3, 16)
        else:
            radius = random.randint(12, 32)
    else:
        size_type = random.random()
        if size_type < 0.7:
            radius = random.randint(4, 25)
        elif size_type < 0.9:
            radius = random.randint(20, 60)
        else:
            radius = random.randint(50, 130)

    x0 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y0 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)
    x1 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y1 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)
    x2 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y2 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)

    return (
        x0,
        y0,
        x1,
        y1,
        x2,
        y2,
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(30, 160),
    )


def initialise():
    shape_count = random.randint(MIN_INITIAL_SHAPES, MAX_INITIAL_SHAPES)
    return [random_shape() for _ in range(shape_count)]


def draw(solution):
    image = PIL.Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))

    for shape in solution:
        x0, y0, x1, y1, x2, y2, r, g, b, alpha = shape
        layer = PIL.Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        canvas = PIL.ImageDraw.Draw(layer, "RGBA")
        canvas.polygon(((x0, y0), (x1, y1), (x2, y2)), fill=(r, g, b, alpha))
        image = PIL.Image.alpha_composite(image, layer)

    return image.convert("RGB")


def mutate_shape(shape, amount=6, detail_mode=False):
    x0, y0, x1, y1, x2, y2, r, g, b, alpha = shape

    if random.random() < 0.08:
        amount *= 4

    mutation_type = random.random()

    if mutation_type < 0.4:
        vertex = random.randrange(3)
        dx = random.randint(-amount, amount)
        dy = random.randint(-amount, amount)

        if vertex == 0:
            x0 = clamp(x0 + dx, 0, WIDTH - 1)
            y0 = clamp(y0 + dy, 0, HEIGHT - 1)
        elif vertex == 1:
            x1 = clamp(x1 + dx, 0, WIDTH - 1)
            y1 = clamp(y1 + dy, 0, HEIGHT - 1)
        else:
            x2 = clamp(x2 + dx, 0, WIDTH - 1)
            y2 = clamp(y2 + dy, 0, HEIGHT - 1)

    elif mutation_type < 0.65:
        dx = random.randint(-amount, amount)
        dy = random.randint(-amount, amount)

        x0 = clamp(x0 + dx, 0, WIDTH - 1)
        y0 = clamp(y0 + dy, 0, HEIGHT - 1)
        x1 = clamp(x1 + dx, 0, WIDTH - 1)
        y1 = clamp(y1 + dy, 0, HEIGHT - 1)
        x2 = clamp(x2 + dx, 0, WIDTH - 1)
        y2 = clamp(y2 + dy, 0, HEIGHT - 1)

    elif mutation_type < 0.9:
        colour_type = random.random()
        full_recolour_chance = 0.01 if detail_mode else 0.05
        all_channel_chance = 0.45 if detail_mode else 0.2

        if colour_type < full_recolour_chance:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)

        elif colour_type < all_channel_chance:
            colour_step = 4 if detail_mode else 5
            r = clamp(r + random.randint(-colour_step, colour_step), 0, 255)
            g = clamp(g + random.randint(-colour_step, colour_step), 0, 255)
            b = clamp(b + random.randint(-colour_step, colour_step), 0, 255)

        else:
            if detail_mode:
                colour_amount = 4 if colour_type < 0.9 else 10
            else:
                colour_amount = 6 if colour_type < 0.85 else 24

            channel = random.randrange(3)
            delta = random.randint(-colour_amount, colour_amount)

            if channel == 0:
                r = clamp(r + delta, 0, 255)
            elif channel == 1:
                g = clamp(g + delta, 0, 255)
            else:
                b = clamp(b + delta, 0, 255)

    else:
        alpha_amount = 4 if random.random() < 0.9 else 16
        alpha = clamp(alpha + random.randint(-alpha_amount, alpha_amount), 5, 160)

    return (x0, y0, x1, y1, x2, y2, r, g, b, alpha)


def shape_add_probability(shape_count):
    if shape_count < 30:
        return 0.25
    if shape_count <= 70:
        return 0.12
    return 0.03


def move_shape_order(solution):
    if len(solution) < 2:
        return solution

    old_index = random.randrange(len(solution))
    shape = solution.pop(old_index)
    shift = random.choice((-3, -2, -1, 1, 2, 3))
    new_index = clamp(old_index + shift, 0, len(solution))
    solution.insert(new_index, shape)

    return solution


def swap_shape_order(solution):
    if len(solution) < 2:
        return solution

    first, second = random.sample(range(len(solution)), 2)
    solution[first], solution[second] = solution[second], solution[first]

    return solution


def replace_worst_shape(solution, detail_mode=False):
    if len(solution) < 2:
        return solution

    candidate_indices = list(range(len(solution) // 2))
    idx = random.choice(candidate_indices)
    solution[idx] = random_shape(detail_mode=detail_mode)

    return solution


def mutation_count_for_fitness(fitness):
    if fitness >= 0.92:
        return random.choices([1, 2, 3], weights=[0.85, 0.13, 0.02])[0]
    if fitness >= 0.87:
        return random.choices([1, 2], weights=[0.82, 0.18])[0]
    return 1


def mutate(
    solution,
    rate=1.0,
    amount=6,
    deletion_probability=0.01,
    add_multiplier=1.0,
    replacement_probability=0.04,
    detail_mode=False,
    z_move_probability=0.12,
    z_swap_probability=0.06,
    fitness=0.0,
):
    mutated = list(solution)

    if mutated and random.random() < rate:
        n_mutations = mutation_count_for_fitness(fitness)

        for _ in range(n_mutations):
            if mutated:
                index = random.randrange(len(mutated))
                mutated[index] = mutate_shape(
                    mutated[index],
                    amount=amount,
                    detail_mode=detail_mode,
                )

    add_probability = min(1.0, shape_add_probability(len(mutated)) * add_multiplier)

    if len(mutated) < MAX_SHAPES and random.random() < add_probability:
        mutated.append(random_shape(detail_mode=detail_mode))

    if mutated and random.random() < replacement_probability:
        if len(mutated) >= 80:
            mutated = replace_worst_shape(mutated, detail_mode=detail_mode)
        else:
            mutated[random.randrange(len(mutated))] = random_shape(
                detail_mode=detail_mode
            )

    if len(mutated) > 1 and random.random() < z_move_probability:
        mutated = move_shape_order(mutated)

    if len(mutated) > 1 and random.random() < z_swap_probability:
        mutated = swap_shape_order(mutated)

    if len(mutated) > 1 and random.random() < deletion_probability:
        del mutated[random.randrange(len(mutated))]

    if not mutated:
        mutated.append(random_shape(detail_mode=detail_mode))

    return mutated


def tournament_pick(population, tournament_size=3):
    competitors = random.sample(population, min(tournament_size, len(population)))
    return max(competitors, key=lambda individual: individual.fitness)


def select(population):
    first = tournament_pick(population)
    second = tournament_pick(population)

    if len(population) > 1:
        attempts = 0

        while second is first and attempts < 5:
            second = tournament_pick(population)
            attempts += 1

    return first, second


def combine(parent_a, parent_b):
    if not parent_a:
        return list(parent_b)

    if not parent_b:
        return list(parent_a)

    cut_a = random.randint(0, len(parent_a))
    cut_b = random.randint(0, len(parent_b))
    child = list(parent_a[:cut_a]) + list(parent_b[cut_b:])

    if len(child) > MAX_SHAPES:
        child = child[:MAX_SHAPES]

    if not child:
        child.append(random_shape())

    return child


def copy_solution(solution):
    return list(solution)


def elite_individuals(population, fraction=0.1):
    count = max(1, round(len(population.individuals) * fraction))

    return sorted(
        population.individuals,
        key=lambda individual: individual.fitness,
        reverse=True,
    )[:count]


def evaluated_individuals(population):
    return [
        individual
        for individual in population.individuals
        if individual.fitness is not None
    ]


def mutation_amount_for_parent(parent):
    if parent.fitness < 0.82:
        return 10
    if parent.fitness < 0.89:
        return 7
    if parent.fitness < 0.93:
        return 4
    if parent.fitness < 0.96:
        return 3
    return 2


def replacement_probability_for_parent(parent):
    if parent.fitness >= 0.90:
        return 0.01
    return 0.04


def detail_mode_for_parent(parent, population):
    return parent.fitness >= 0.87 or population.current_best.fitness >= 0.87


def deletion_probability_for_parent(parent):
    if parent.fitness >= 0.90:
        return 0.015
    if parent.fitness >= 0.85:
        return 0.025
    return 0.01


def choose_parent(elites, population, best_fitness):
    elite_bias = 0.75 if best_fitness >= 0.90 else 0.90

    if random.random() < elite_bias:
        return random.choice(elites)

    return random.choice(evaluated_individuals(population))


def update_stagnation_state(population, generation):
    current_best = population.current_best.fitness

    if not hasattr(population, "_last_stagnation_check_best"):
        population._last_stagnation_check_best = current_best

    if not hasattr(population, "_stagnation_boost_until"):
        population._stagnation_boost_until = 0

    if generation % 100 == 0:
        improvement = current_best - population._last_stagnation_check_best

        if improvement < 0.003:
            population._stagnation_boost_until = generation + 50

        population._last_stagnation_check_best = current_best


def stagnation_boost_active(population, generation):
    return generation <= getattr(population, "_stagnation_boost_until", 0)


def evolve(population, args):
    original_size = population.intended_size
    elites = elite_individuals(population)
    offspring_count = original_size * 3
    generation = population.generation + 1
    best_fitness = population.current_best.fitness

    update_stagnation_state(population, generation)
    boost = stagnation_boost_active(population, generation)

    for _ in range(offspring_count):
        parent = choose_parent(elites, population, best_fitness)
        amount = mutation_amount_for_parent(parent)
        add_multiplier = 1.0
        detail_mode = detail_mode_for_parent(parent, population)
        replacement_probability = replacement_probability_for_parent(parent)
        z_move_probability = 0.14 if detail_mode else 0.12
        z_swap_probability = 0.08 if detail_mode else 0.06

        if boost:
            amount += 2
            add_multiplier = 1.25

            if not detail_mode:
                replacement_probability = 0.06

        deletion_probability = deletion_probability_for_parent(parent)

        offspring = mutate(
            copy_solution(parent.chromosome),
            amount=amount,
            deletion_probability=deletion_probability,
            add_multiplier=add_multiplier,
            replacement_probability=replacement_probability,
            detail_mode=detail_mode,
            z_move_probability=z_move_probability,
            z_swap_probability=z_swap_probability,
            fitness=parent.fitness,
        )

        population.individuals.append(Individual(offspring))

    population.generation += 1

    return population.evaluate(lazy=True).survive(n=original_size)
