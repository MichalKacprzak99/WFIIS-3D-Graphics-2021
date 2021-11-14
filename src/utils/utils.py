from src.square import Square


def calculate_velocity(left_object: Square, right_object: Square):
    return ((left_object.mass - right_object.mass) / (left_object.mass + right_object.mass)) * left_object.vel \
           + ((2 * right_object.mass) / (left_object.mass + right_object.mass)) * right_object.vel
