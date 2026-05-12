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


def random_radius():
    size_type = random.random()

    if size_type < 0.7:
        return random.randint(4, 25)
    if size_type < 0.9:
        return random.randint(20, 60)
    return random.randint(50, 130)


def random_colour():
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(30, 160),
    )


def random_triangle():
    centre_x = random.randint(0, WIDTH - 1)
    centre_y = random.randint(0, HEIGHT - 1)
    radius = random_radius()

    x0 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y0 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)
    x1 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y1 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)
    x2 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y2 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)

    return (
        "triangle",
        x0,
        y0,
        x1,
        y1,
        x2,
        y2,
        *random_colour(),
    )


def random_ellipse():
    centre_x = random.randint(0, WIDTH - 1)
    centre_y = random.randint(0, HEIGHT - 1)
    radius = random_radius()
    rx = random.randint(max(2, radius // 3), radius)
    ry = random.randint(max(2, radius // 3), radius)
    x0 = clamp(centre_x - rx, 0, WIDTH - 1)
    y0 = clamp(centre_y - ry, 0, HEIGHT - 1)
    x1 = clamp(centre_x + rx, 0, WIDTH - 1)
    y1 = clamp(centre_y + ry, 0, HEIGHT - 1)

    return (
        "ellipse",
        x0,
        y0,
        x1,
        y1,
        *random_colour(),
    )


def random_line():
    centre_x = random.randint(0, WIDTH - 1)
    centre_y = random.randint(0, HEIGHT - 1)
    radius = random_radius()
    x0 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y0 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)
    x1 = clamp(centre_x + random.randint(-radius, radius), 0, WIDTH - 1)
    y1 = clamp(centre_y + random.randint(-radius, radius), 0, HEIGHT - 1)
    width = random.randint(1, 8)

    return (
        "line",
        x0,
        y0,
        x1,
        y1,
        width,
        *random_colour(),
    )


def evolution_stage(best_fitness):
    if best_fitness < 0.75:
        return "early"
    if best_fitness < 0.85:
        return "middle"
    return "late"


def random_shape(stage="early"):
    shape_type = random.random()

    if stage == "late":
        if shape_type < 0.7:
            return random_triangle()
        if shape_type < 0.75:
            return random_ellipse()
        return random_line()

    if stage == "middle":
        if shape_type < 0.6:
            return random_triangle()
        if shape_type < 0.8:
            return random_ellipse()
        return random_line()

    if shape_type < 0.5:
        return random_triangle()
    if shape_type < 0.85:
        return random_ellipse()
    return random_line()


def initialise():
    shape_count = random.randint(MIN_INITIAL_SHAPES, MAX_INITIAL_SHAPES)
    return [random_shape() for _ in range(shape_count)]


def draw(solution):
    image = PIL.Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))

    for shape in solution:
        shape_type = shape[0]
        layer = PIL.Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        canvas = PIL.ImageDraw.Draw(layer, "RGBA")
        if shape_type == "triangle":
            _, x0, y0, x1, y1, x2, y2, r, g, b, alpha = shape
            canvas.polygon(((x0, y0), (x1, y1), (x2, y2)), fill=(r, g, b, alpha))
        elif shape_type == "ellipse":
            _, x0, y0, x1, y1, r, g, b, alpha = shape
            canvas.ellipse((x0, y0, x1, y1), fill=(r, g, b, alpha))
        elif shape_type == "line":
            _, x0, y0, x1, y1, width, r, g, b, alpha = shape
            canvas.line((x0, y0, x1, y1), fill=(r, g, b, alpha), width=width)
        image = PIL.Image.alpha_composite(image, layer)

    return image.convert("RGB")


def mutation_amount(stage):
    if stage == "early":
        return 8
    if stage == "middle":
        return 6
    return 3


def mutate_colour(r, g, b, stage):
    colour_type = random.random()
    if colour_type < 0.05:
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    if stage == "late":
        colour_amount = 4 if colour_type < 0.9 else 12
    elif stage == "middle":
        colour_amount = 6 if colour_type < 0.85 else 24
    else:
        colour_amount = 8 if colour_type < 0.8 else 32

    channel = random.randrange(3)
    delta = random.randint(-colour_amount, colour_amount)
    if channel == 0:
        r = clamp(r + delta, 0, 255)
    elif channel == 1:
        g = clamp(g + delta, 0, 255)
    else:
        b = clamp(b + delta, 0, 255)
    return r, g, b


def mutate_alpha(alpha, stage):
    if stage == "late":
        alpha_amount = 3 if random.random() < 0.9 else 8
    elif stage == "middle":
        alpha_amount = 4 if random.random() < 0.9 else 16
    else:
        alpha_amount = 6 if random.random() < 0.85 else 20
    return clamp(alpha + random.randint(-alpha_amount, alpha_amount), 10, 160)


def mutate_triangle(shape, amount, stage):
    _, x0, y0, x1, y1, x2, y2, r, g, b, alpha = shape
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
        r, g, b = mutate_colour(r, g, b, stage)
    else:
        alpha = mutate_alpha(alpha, stage)

    return ("triangle", x0, y0, x1, y1, x2, y2, r, g, b, alpha)


def mutate_ellipse(shape, amount, stage):
    _, x0, y0, x1, y1, r, g, b, alpha = shape
    mutation_type = random.random()

    if mutation_type < 0.35:
        dx = random.randint(-amount, amount)
        dy = random.randint(-amount, amount)
        x0 = clamp(x0 + dx, 0, WIDTH - 1)
        y0 = clamp(y0 + dy, 0, HEIGHT - 1)
        x1 = clamp(x1 + dx, 0, WIDTH - 1)
        y1 = clamp(y1 + dy, 0, HEIGHT - 1)
    elif mutation_type < 0.65:
        edge = random.randrange(4)
        delta = random.randint(-amount, amount)
        if edge == 0:
            x0 = clamp(x0 + delta, 0, WIDTH - 1)
        elif edge == 1:
            y0 = clamp(y0 + delta, 0, HEIGHT - 1)
        elif edge == 2:
            x1 = clamp(x1 + delta, 0, WIDTH - 1)
        else:
            y1 = clamp(y1 + delta, 0, HEIGHT - 1)
    elif mutation_type < 0.9:
        r, g, b = mutate_colour(r, g, b, stage)
    else:
        alpha = mutate_alpha(alpha, stage)

    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    if x0 == x1:
        x1 = clamp(x0 + 1, 0, WIDTH - 1)
        x0, x1 = sorted((x0, x1))
    if y0 == y1:
        y1 = clamp(y0 + 1, 0, HEIGHT - 1)
        y0, y1 = sorted((y0, y1))

    return ("ellipse", x0, y0, x1, y1, r, g, b, alpha)


def mutate_line(shape, amount, stage):
    _, x0, y0, x1, y1, width, r, g, b, alpha = shape
    mutation_type = random.random()

    if mutation_type < 0.35:
        if random.random() < 0.5:
            x0 = clamp(x0 + random.randint(-amount, amount), 0, WIDTH - 1)
            y0 = clamp(y0 + random.randint(-amount, amount), 0, HEIGHT - 1)
        else:
            x1 = clamp(x1 + random.randint(-amount, amount), 0, WIDTH - 1)
            y1 = clamp(y1 + random.randint(-amount, amount), 0, HEIGHT - 1)
    elif mutation_type < 0.55:
        dx = random.randint(-amount, amount)
        dy = random.randint(-amount, amount)
        x0 = clamp(x0 + dx, 0, WIDTH - 1)
        y0 = clamp(y0 + dy, 0, HEIGHT - 1)
        x1 = clamp(x1 + dx, 0, WIDTH - 1)
        y1 = clamp(y1 + dy, 0, HEIGHT - 1)
    elif mutation_type < 0.7:
        width = clamp(width + random.choice((-1, 1)), 1, 8)
    elif mutation_type < 0.92:
        r, g, b = mutate_colour(r, g, b, stage)
    else:
        alpha = mutate_alpha(alpha, stage)

    return ("line", x0, y0, x1, y1, width, r, g, b, alpha)


def mutate_shape(shape, stage="early"):
    amount = mutation_amount(stage)
    jump_chance = 0.1 if stage == "early" else 0.08 if stage == "middle" else 0.02
    if random.random() < jump_chance:
        amount *= 4

    shape_type = shape[0]
    if shape_type == "triangle":
        return mutate_triangle(shape, amount, stage)
    if shape_type == "ellipse":
        return mutate_ellipse(shape, amount, stage)
    if shape_type == "line":
        return mutate_line(shape, amount, stage)
    return random_shape(stage)


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


def mutate(solution, rate=1.0, stage="early"):
    mutated = list(solution)

    if mutated and random.random() < rate:
        index = random.randrange(len(mutated))
        mutated[index] = mutate_shape(mutated[index], stage)

    if len(mutated) < MAX_SHAPES and random.random() < shape_add_probability(len(mutated)):
        mutated.append(random_shape(stage))

    if mutated and random.random() < 0.04:
        replace_rate = 0.02 if stage == "late" else 0.04
        if random.random() < replace_rate / 0.04:
            mutated[random.randrange(len(mutated))] = random_shape(stage)

    if len(mutated) > 1 and random.random() < 0.12:
        mutated = move_shape_order(mutated)

    if len(mutated) > 1 and random.random() < 0.06:
        mutated = swap_shape_order(mutated)

    if len(mutated) > 1 and random.random() < 0.01:
        del mutated[random.randrange(len(mutated))]

    if not mutated:
        mutated.append(random_shape())

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
    return sorted(population.individuals, key=lambda individual: individual.fitness, reverse=True)[:count]


def evolve(population, args):
    original_size = population.intended_size
    elites = elite_individuals(population)
    offspring_count = original_size * 2
    stage = evolution_stage(population.current_best.fitness)

    for _ in range(offspring_count):
        parent = random.choice(elites)
        offspring = mutate(copy_solution(parent.chromosome), stage=stage)
        population.individuals.append(Individual(offspring))

    population.generation += 1
    return population.evaluate(lazy=True).survive(n=original_size)
