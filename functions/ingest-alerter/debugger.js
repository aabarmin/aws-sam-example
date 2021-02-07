const { lambdaHandler } = require('./app');

const event = {
    startDate: '2020-10-20',
    endDate: '2020-10-21'
};
lambdaHandler(event).then(m => {
    console.log(m)
})