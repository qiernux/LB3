from flask import Flask, jsonify, request
from functools import wraps

app = Flask(__name__)


# Класс для представления блюда
class Dish:
   def __init__(self, id, name, price, ingredients):
       self.id = id
       self.name = name
       self.price = price
       self.ingredients = ingredients

   def to_dict(self):
       return {
           "id": self.id,
           "name": self.name,
           "price": self.price,
           "ingredients": self.ingredients
       }


# Класс для управления меню
class Menu:
   def __init__(self):
       self.dishes = {}
       self.next_id = 1

   def add_dish(self, name, price, ingredients):
       dish = Dish(self.next_id, name, price, ingredients)
       self.dishes[self.next_id] = dish
       self.next_id += 1
       return dish

   def get_dish(self, id):
       return self.dishes.get(id)

   def update_dish(self, id, name=None, price=None, ingredients=None):
       dish = self.dishes.get(id)
       if dish:
           if name:
               dish.name = name
           if price:
               dish.price = price
           if ingredients:
               dish.ingredients = ingredients
       return dish

   def delete_dish(self, id):
       if id in self.dishes:
           del self.dishes[id]
           return True
       return False

   def filter_by_price(self, max_price):
       return [dish.to_dict() for dish in self.dishes.values() if float(dish.price) <= max_price]


# Инициализация меню
menu = Menu()

# Добавление начальных блюд
menu.add_dish("Пицца Маргарита", "9.99", "Томаты, моцарелла")
menu.add_dish("Пицца Квартро Формаджи", "12.99", "Четыре вида сыра")
menu.add_dish("Пицца Мясная", "14.99", "Пепперони, колбаса, бекон")

# Легкое хранение пользователей
users = {"admin": "password"}


# Функция для базовой аутентификации
def check_auth(username, password):
   return username in users and users[username] == password


def authenticate():
   return jsonify({"message": "Authentication required"}), 401


def requires_auth(f):
   @wraps(f)
   def decorated(*args, **kwargs):
       auth = request.authorization
       if not auth or not check_auth(auth.username, auth.password):
           return authenticate()
       return f(*args, **kwargs)

   return decorated


@app.route('/menu', methods=['GET', 'POST'])
@requires_auth
def manage_menu():
   if request.method == 'POST':
       data = request.get_json()

       # Проверка наличия необходимых полей
       if 'name' not in data or 'price' not in data or 'ingredients' not in data:
           return jsonify({"error": "Missing dish data"}), 400

       dish = menu.add_dish(data['name'], data['price'], data['ingredients'])
       return jsonify(dish.to_dict()), 201

   # Возвращение списка всех блюд
   return jsonify([dish.to_dict() for dish in menu.dishes.values()])


@app.route('/menu/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
def dish_detail(id):
   if request.method == 'GET':
       dish = menu.get_dish(id)
       if dish is None:
           return jsonify({"error": "Dish not found"}), 404
       return jsonify(dish.to_dict())

   elif request.method == 'PUT':
       data = request.get_json()

       if id not in menu.dishes:
           return jsonify({"error": "Dish not found"}), 404

       dish = menu.update_dish(id, data.get('name'), data.get('price'), data.get('ingredients'))
       return jsonify(dish.to_dict())

   elif request.method == 'DELETE':
       if menu.delete_dish(id):
           return jsonify({"result": "Dish deleted"})
       return jsonify({"error": "Dish not found"}), 404


@app.route('/menu/filter', methods=['GET'])
@requires_auth
def filter_menu():
   max_price = request.args.get('max_price', type=float)
   if max_price is None:
       return jsonify({"error": "Missing max_price parameter"}), 400

   filtered_dishes = menu.filter_by_price(max_price)
   return jsonify(filtered_dishes)


if __name__ == '__main__':
   app.run(port=8000, debug=True)  # Запуск сервера на порту 8000
