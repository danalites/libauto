curl -XPOST http://localhost:8868/parse --data 'locale=en_US&text="My number is 4111-1111-1111-1111. card"&dims="["credit-card-number"]"'

echo "\n-----\n"

curl -XPOST http://localhost:8868/parse --data 'locale=en_US&text="7932742"&dims="["Ordinal"]"'