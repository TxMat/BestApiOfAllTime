import './App.css';
import ApiCallComponent from "./components/ApiCallComponent";

let orderPostJson = [{"products": [{"id": 1, "quantity": 2}, {"id": 2, "quantity": 1},]}]

let orderPutJson = [{
    "order": {
        "email": "jgnault@uqac.ca", "shipping_information": {
            "country": "Canada",
            "address": "201, rue Président-Kennedy",
            "postal_code": "G7X 3Y7",
            "city": "Chicoutimi",
            "province": "QC"
        }
    }
}, {
    "credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2024,
        "cvv": "123",
        "expiration_month": 9
    }
},
{
    "credit_card": {
        "name": "John Doe",
        "number": "4000 0000 0000 0002",
        "expiration_year": 2024,
        "cvv": "123",
        "expiration_month": 9
    }
},
{
    "credit_card": {
        "name": "John Doe",
        "number": "1111 2222 3333 4444",
        "expiration_year": 2024,
        "cvv": "123",
        "expiration_month": 9
    }
}]

function App() {
    return (<div className="App">
        <header className="mt-8">
            <h1 className="text-5xl bg-clip-text text-transparent bg-gradient-to-tr from-info via-indigo-400 to-success">Best
                Api Call Test</h1>
        </header>
        <div className="divider mx-8 divide-accent"></div>
        <div className="grid grid-rows-1 gap-4 mx-8 mb-8">
            <ApiCallComponent displayName="/" routeName="/" disablePayload={true} allowedRoutes={["GET"]}/>
            <ApiCallComponent displayName="/Order" routeName="/order" allowedRoutes={["POST"]}
                              defaultJson={orderPostJson}/>
            <ApiCallComponent displayName="/Order/" routeName="/order/" allowedRoutes={["GET", "PUT"]}
                              defaultJson={orderPutJson} displayOrderId={true}/>
        </div>
    </div>);
}

export default App;
