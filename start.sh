#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="mysql"
IMAGE="mysql:8.0"
ROOTPW="MyNewRootPW!ChangeMe"
WEBAPP_PW="webapp-user"
DB_NAME="web_app"

export VIRT_LAB_DB="0"

echo "Pulling git changes..."
git pull

echo "Removing any previous container named $CONTAINER_NAME..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo "Starting new MySQL container..."
docker run --name "$CONTAINER_NAME" \
  -e MYSQL_ROOT_PASSWORD="$ROOTPW" \
  -v mysql-data:/var/lib/mysql \
  -p 3306:3306 \
  -d "$IMAGE"

echo "Waiting for MySQL (TCP) to be ready..."
for i in {1..60}; do
  if docker exec "$CONTAINER_NAME" mysqladmin ping -h 127.0.0.1 -uroot -p"$ROOTPW" --silent &>/dev/null; then
    echo "MySQL is ready."
    break
  fi
  echo "  attempt $i: waiting..."
  sleep 2
  if [ $i -eq 60 ]; then
    echo "MySQL did not become ready in time." >&2
    docker logs --tail 200 "$CONTAINER_NAME"
    exit 1
  fi
done

docker exec -i "$CONTAINER_NAME" mysql -uroot -p"$ROOTPW" --protocol=TCP -h 127.0.0.1 -e "
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'webapp'@'%' IDENTIFIED BY '$WEBAPP_PW';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO 'webapp'@'%';
FLUSH PRIVILEGES;
"

echo "Database and user created. Test connecting as webapp:"
docker exec -i "$CONTAINER_NAME" mysql -h 127.0.0.1 -P 3306 -u webapp -p"$WEBAPP_PW" -D "$DB_NAME" -e "SHOW TABLES;"

venv_dir="/tmp/test_env_$(python3 --version 2>&1)"

if [ ! -d "$venv_dir" ]; then
    echo "Virtual environment not found — creating one..."
    python3 -m venv "$venv_dir"
else
    echo "Virtual environment already exists — reusing it."
fi

source "$venv_dir/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
python3 init_db.py

echo "Starting Flask (debug) — if you want this to run in background, run it separately."
flask --debug --app=server run
