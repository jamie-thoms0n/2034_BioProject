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


def random_shape():
    x0 = random.randint(0, WIDTH - 1)
    y0 = random.randint(0, HEIGHT - 1)
    x1 = random.randint(0, WIDTH - 1)
    y1 = random.randint(0, HEIGHT - 1)
    x2 = random.randint(0, WIDTH - 1)
    y2 = random.randint(0, HEIGHT - 1)

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
        random.randint(20, 120),
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


def mutate_shape(shape, amount=4):
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
        colour_amount = 6 if random.random() < 0.9 else 24
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
        alpha = clamp(alpha + random.randint(-alpha_amount, alpha_amount), 10, 160)

    return (x0, y0, x1, y1, x2, y2, r, g, b, alpha)


def shape_add_probability(shape_count):
    if shape_count < 25:
        return 0.35
    if shape_count < 60:
        return 0.18
    if shape_count < 90:
        return 0.08
    return 0.02


def move_shape_order(solution):
    if len(solution) < 2:
        return solution

    old_index = random.randrange(len(solution))
    shape = solution.pop(old_index)
    shift = random.choice((-3, -2, -1, 1, 2, 3))
    new_index = clamp(old_index + shift, 0, len(solution))
    solution.insert(new_index, shape)
    return solution


def mutate(solution, rate=1.0):
    mutated = list(solution)

    if mutated and random.random() < rate:
        index = random.randrange(len(mutated))
        mutated[index] = mutate_shape(mutated[index])

    if len(mutated) < MAX_SHAPES and random.random() < shape_add_probability(len(mutated)):
        mutated.append(random_shape())

    if mutated and random.random() < 0.04:
        mutated[random.randrange(len(mutated))] = random_shape()

    if len(mutated) > 1 and random.random() < 0.08:
        mutated = move_shape_order(mutated)

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


def elite_individuals(population, fraction=0.2):
    count = max(1, round(len(population.individuals) * fraction))
    return sorted(population.individuals, key=lambda individual: individual.fitness, reverse=True)[:count]


def evolve(population, args):
    original_size = population.intended_size
    elites = elite_individuals(population)
    offspring_count = original_size

    for _ in range(offspring_count):
        parent = random.choice(elites)
        offspring = mutate(copy_solution(parent.chromosome))
        population.individuals.append(Individual(offspring))

    population.generation += 1
    return population.evaluate(lazy=True).survive(n=original_size)
