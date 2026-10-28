// Shared frontend utility functions.

function safeFileName(
    value
) {

    return value
        .replace(
            /[^A-Za-z0-9]+/g,
            "_"
        )
        .replace(
            /^_+|_+$/g,
            ""
        );
}


function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value || "";


    return div.innerHTML;
}


function formatApiError(
    data,
    fallback = "An unexpected error occurred."
) {

    if (!data) {
        return fallback;
    }


    // FastAPI detail as a normal string.
    if (
        typeof data.detail === "string"
    ) {
        return data.detail;
    }


    // FastAPI 422 validation errors.
    if (
        Array.isArray(data.detail)
    ) {

        return data.detail
            .map(item => {

                if (
                    typeof item === "string"
                ) {
                    return item;
                }


                const location =
                    Array.isArray(item.loc)
                    ? item.loc.join(" → ")
                    : "";


                const message =
                    item.msg ||
                    item.message ||
                    JSON.stringify(item);


                if (location) {

                    return `${location}: ${message}`;
                }


                return message;

            })
            .join("\n");
    }


    // Structured error object.
    if (
        data.detail &&
        typeof data.detail === "object"
    ) {

        if (
            typeof data.detail.message === "string"
        ) {
            return data.detail.message;
        }


        try {

            return JSON.stringify(
                data.detail,
                null,
                2
            );

        } catch {
            return fallback;
        }
    }


    if (
        typeof data.message === "string"
    ) {

        return data.message;
    }


    if (
        typeof data.error === "string"
    ) {

        return data.error;
    }


    return fallback;
}


async function downloadFile(
    endpoint,
    formData,
    filename
) {

    const response =
        await fetch(
            endpoint,
            {
                method: "POST",
                body: formData
            }
        );


    if (!response.ok) {

        alert(
            "Could not create the Word document."
        );

        return;
    }


    const blob =
        await response.blob();


    const url =
        URL.createObjectURL(
            blob
        );


    const link =
        document.createElement(
            "a"
        );


    link.href = url;

    link.download =
        filename;


    document.body.appendChild(
        link
    );


    link.click();

    link.remove();


    URL.revokeObjectURL(
        url
    );
}


function el(id) {
    return document.getElementById(id);
}
