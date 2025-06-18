class User {
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.email = data.email;
  }

  toNeo4jProperties() {
    return {
      id: this.id,
      name: this.name,
      email: this.email
    };
  }
}

module.exports = User;