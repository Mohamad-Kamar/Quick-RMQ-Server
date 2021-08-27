const http = require("http");
const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
    let data = '';
    req.on('data', chunk => {
      data += chunk;
    })
    req.on('end', () => {
      console.log(JSON.stringify(JSON.parse(data),null,2)); // 'Buy the milk'
      res.end("=========================================");
    })
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
//"/execute/entities/v1.1/bi" + "/yang/bi/mpls/bi-services"
