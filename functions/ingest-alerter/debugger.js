const { lambdaHandler } = require('./app');

lambdaHandler().then(m => {
    console.log(m)
})