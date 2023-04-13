import {useEffect, useState} from "react";
import ReactJson from "react-json-view";


const tabClass = "tab tab-lg text-info tab-border-none tab-lifted";
const tabDisabled = "tab tab-lg text-base-100 tab-border-none tab-lifted tab-disabled";
const activeTabClass = "tab tab-border-none tab-active tab-lg text-info tab-lifted";

function ApiCallComponent(props) {


    const [activeTab, setActiveTab] = useState(props.allowedRoutes[0]);
    const [rep, setRep] = useState(new Response());
    const [responseJson, setResponseJson] = useState({});
    const [orderId, setOrderId] = useState(1);
    const [payloadJson, setPayloadJson] = useState(props.defaultJson ? props.defaultJson[0] : {});
    const [borderColor, setBorderColor] = useState("border border-accent");
    const [textColor, setTextColor] = useState("text-accent");

    function callApi(method) {

        setResponseJson({});

        let apiUrl = process.env.FLASK_API_URL ? process.env.FLASK_API_URL : "http://127.0.0.1:5000"

        if (props.routeName === "/order/") {
            apiUrl = apiUrl + props.routeName + orderId
        } else {
            apiUrl = apiUrl + props.routeName
        }

        if (method === "GET") {
            fetch(apiUrl, {method: method})
                .then(response => {
                    setRep(response)
                    return response.json()
                })
                .then(response => setResponseJson(response))
        } else {
            fetch(apiUrl, {
                method: method, headers: {
                    'Content-Type': 'application/json'
                }, body: JSON.stringify(payloadJson)
            })
                .then(response => {
                    setRep(response)
                    return response.json()
                })
                .then(response => setResponseJson(response))
        }


    }

    function updateBorderColor(status) {
        let color = "border border-error";
        if (status >= 200 && status < 300) {
            color = "border border-success";
        } else if (status === 404) {
            color = "border border-warning";
        } else if (status >= 400 && status < 500) {
            color = "border border-error";
        } else if (status >= 500) {
            color = "border border-error";
        }
        setBorderColor(color);
    }

    function updateTextColor(status) {
        let color = "text-error";
        if (status >= 200 && status < 300) {
            color = "text-success";
        } else if (status === 404) {
            color = "text-warning";
        } else if (status >= 400 && status < 500) {
            color = "text-error";
        } else if (status >= 500) {
            color = "text-error";
        }
        setTextColor(color);
    }

    useEffect(() => {
        console.log(rep)
        console.log(payloadJson)
        updateBorderColor(rep.status)
        updateTextColor(rep.status)
    }, [rep])

    function handleReset() {
        setResponseJson({});
        setPayloadJson(props.defaultJson ? props.defaultJson[0] : {});
    }

    function jsonDisplayer() {
        if (activeTab === "GET") {
            return <div className="text-center">No Json Payload Required</div>
        } else {
            // bigger font size
            return <ReactJson
                src={payloadJson}
                theme="ocean"
                iconStyle={"circle"}
                name={false}
                style={{
                    borderRadius: "0.5rem",
                }}
                onAdd={(add) => {
                    setPayloadJson(add.updated_src)
                }}
                onEdit={(edit) => {
                    setPayloadJson(edit.updated_src)
                }}
                onDelete={(del) => {
                    setPayloadJson(del.updated_src)
                }}/>


        }
    }

    function generateDisplayName() {
        if (props.routeName === "/order/") {
            return props.displayName + orderId
        } else {
            return props.displayName
        }
    }

    function jsonTabManager() {
        if (props.defaultJson && props.defaultJson.length > 1) {
            return <div className="">
                <div className="tabs">
                    <button className="tab" onClick={() => setPayloadJson(props.defaultJson[0])}>Shipping Info
                    </button>
                    <button className="tab" onClick={() => setPayloadJson(props.defaultJson[1])}>Valid Billing Info
                    </button>
                    <button className="tab" onClick={() => setPayloadJson(props.defaultJson[2])}>Declined Billing Info
                    </button>
                    <button className="tab" onClick={() => setPayloadJson(props.defaultJson[3])}>Incorrect Billing Info
                    </button>
                </div>
            </div>
        }
    }

    return (<div className="collapse collapse-arrow border border-base-300 bg-base-200 rounded-box">
        <input type="checkbox"/>
        <div className="collapse-title text-xl font-medium pl-12">
            <h2>{generateDisplayName()}</h2>
        </div>
        <div className="collapse-content">
            <div className="rounded-box bg-base-300">
                <div className="navbar">
                    <div className="tabs navbar-start">
                        <button
                            className={props.allowedRoutes.includes("GET") ? activeTab === "GET" ? activeTabClass : tabClass : tabDisabled}
                            onClick={() => props.allowedRoutes.includes("GET") ? setActiveTab("GET") : null}>GET
                        </button>
                        <button
                            className={props.allowedRoutes.includes("POST") ? activeTab === "POST" ? activeTabClass : tabClass : tabDisabled}
                            onClick={() => props.allowedRoutes.includes("POST") ? setActiveTab("POST") : null}>POST
                        </button>
                        <button
                            className={props.allowedRoutes.includes("PUT") ? activeTab === "PUT" ? activeTabClass : tabClass : tabDisabled}
                            onClick={() => props.allowedRoutes.includes("PUT") ? setActiveTab("PUT") : null}>PUT
                        </button>
                    </div>
                    <div className="navbar-center">
                        <div className="card-title">
                            <h2 className="mx-auto">Query Builder</h2>
                        </div>
                    </div>
                    <div className="navbar-end">
                        <input type="number" placeholder="Order Id"
                               className={props.displayOrderId ? "input input-bordered input-info w-48 mr-16 mt-4" : "hidden"}
                               onChange={event => setOrderId(event.target.value)}/>
                    </div>
                </div>
                <div className="grid grid-cols-3 h-full mx-12 justify-items-stretch">
                    <div className="px-6 mt-2 mb-10">
                        <h3 className="">Json Payload</h3>
                        <div
                            className="text-left p-4 border bg-base-200 border-2 rounded-box h-full max-h-[600px] rounded-box border border-accent">
                            {jsonDisplayer()}
                        </div>
                        {jsonTabManager()}
                    </div>
                    <div className="grid grid-rows-2 justify-center">
                        <button className="btn btn-success btn-lg self-end mb-2"
                                onClick={(event) => callApi(activeTab)}>Send
                        </button>
                        <button className="btn btn-error mt-2" onClick={(event) => handleReset()}>Reset
                        </button>
                    </div>
                    <div className="px-6 mt-2 mb-10">
                        <h3 className="">Response</h3>
                        <div
                            className={borderColor + " p-4 border bg-base-200 border-2 rounded-box text-left h-full min-h-[600px] max-h-[600px] overflow-y-scroll scrollbar-thin scrollbar-thumb-sky-800 scrollbar-thumb-rounded-full scrollbar-track-rounded-full"}>
                            <ReactJson
                                src={responseJson}
                                iconStyle={"circle"}
                                theme="ocean"
                                style={{
                                    borderRadius: "0.5rem",
                                }}
                                name={false}
                            />
                        </div>
                        <h3 className={textColor + " mt-2"}>Status Code: {rep.status}</h3>
                    </div>
                </div>
            </div>
        </div>
    </div>);
}

export default ApiCallComponent;