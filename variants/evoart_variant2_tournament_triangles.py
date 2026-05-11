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


def mutate_shape(shape, amount=15):
    x0, y0, x1, y1, x2, y2, r, g, b, alpha = shape

    if random.random() < 0.6:
        x0 = clamp(x0 + random.randint(-amount, amount), 0, WIDTH - 1)
    if random.random() < 0.6:
        y0 = clamp(y0 + random.randint(-amount, amount), 0, HEIGHT - 1)
    if random.random() < 0.6:
        x1 = clamp(x1 + random.randint(-amount, amount), 0, WIDTH - 1)
    if random.random() < 0.6:
        y1 = clamp(y1 + random.randint(-amount, amount), 0, HEIGHT - 1)
    if random.random() < 0.6:
        x2 = clamp(x2 + random.randint(-amount, amount), 0, WIDTH - 1)
    if random.random() < 0.6:
        y2 = clamp(y2 + random.randint(-amount, amount), 0, HEIGHT - 1)

    if random.random() < 0.6:
        r = clamp(r + random.randint(-amount, amount), 0, 255)
    if random.random() < 0.6:
        g = clamp(g + random.randint(-amount, amount), 0, 255)
    if random.random() < 0.6:
        b = clamp(b + random.randint(-amount, amount), 0, 255)
    if random.random() < 0.6:
        alpha = clamp(alpha + random.randint(-10, 10), 10, 160)

    return (x0, y0, x1, y1, x2, y2, r, g, b, alpha)


def mutate(solution, rate=0.2):
    mutated = list(solution)

    for index, shape in enumerate(mutated):
        if random.random() < rate:
            mutated[index] = mutate_shape(shape)

    if len(mutated) < MAX_SHAPES and random.random() < 0.15:
        mutated.append(random_shape())

    if len(mutated) > 1 and random.random() < 0.05:
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


def evolve(population, args):
    return (
        population.survive(fraction=0.4)
        .breed(select, combine)
        .mutate(mutate, probability=0.8, rate=0.25)
        .evaluate()
    )
