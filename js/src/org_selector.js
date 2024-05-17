import { Select } from "antd"
import { useEffect, useState } from "react"

export const OrgSelector = () => {
    const [orgs, setOrgs] = useState()
    const [defaultOrg, setDefaultOrg] = useState(localStorage.getItem("org_id"))

    const loadOrgs = () => {

        fetch("/api/v1/organizations")
            .then(res => res.json())
            .then(data => {
                if (defaultOrg === null) {
                    /*data.data.map(org => {
                        if (org.is_primary) {
                            console.log(org.id)
                            setDefaultOrg(org.id)
                        }
                    })*/
                    
                    setDefaultOrg(data.data[0].id)
                }

                setOrgs(data.data)
            })
    }

    const changeOrg = (orgId) => {
        localStorage.setItem('org_id', orgId)
        document.location.reload()
    }

    useEffect(() => {
        loadOrgs()
    }, [])

    return (
        <Select
            defaultValue={defaultOrg}
            placeholder="Select an organization"
            options={orgs?.map(org => ({
                value: org.id,
                label: org.display_name
            }))}
            onChange={changeOrg}
            style={{width: 200}}
        />
    )
}