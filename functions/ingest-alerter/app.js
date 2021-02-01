const axios = require('axios');
const xpath = require('xpath');
const DOMParser = require('xmldom').DOMParser;

exports.lambdaHandler = async (event, context) => {
    return new Promise((resolve, reject) => {
        const params = {
            method: 'get',
            url: 'https://publications.europa.eu/webapi/notification/ingestion?startDate=2020-10-01&endDate=2020-10-02&type=CREATE&wemiClasses=work',
            headers: {
                'Accept-Language': 'en_EN',
                'Accept': '*/*'
            }
        };
        axios(params)
            .then(response => {
                const xmlContent = response.data;
                const parser = new DOMParser();
                const document = parser.parseFromString(xmlContent);
                const nodes = xpath.select('//*[local-name(.)="cellarId"]/text()', document);
                const cellarIds = new Set();
                for (let i = 0; i < nodes.length; i++) {
                    const node = nodes[i];
                    const cellarId = node.nodeValue.substring(7);
                    cellarIds.add(cellarId);
                }
                const items = Array.from(cellarIds)
                    .map(cellar => {
                        return { cellarId: cellar}
                    });
                resolve({
                    items: items
                })
            })
            .catch(error => {
                reject(error.message);
            });
    });
};